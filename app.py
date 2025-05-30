from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from config import Config
from models import db, Device, BorrowRecord, ApprovalRecord, User, Log

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# 配置数据库URI
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DB}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def log_action(user_id, action, details):
    """记录操作日志"""
    log = Log(user_id=user_id, action=action, details=details)
    db.session.add(log)
    db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/borrow_and_return')
def borrow_and_return():
    try:
        # 获取可借用的设备
        available_devices = Device.query.filter_by(can_borrow=1, status=1).all()
        # 获取当前用户借用的设备
        user_id = session.get('user_id', 1)  # 临时使用测试用户ID
        borrowed_devices = db.session.query(Device, BorrowRecord).join(
            BorrowRecord, Device.device_id == Device.device_id
        ).filter(
            BorrowRecord.user_id == user_id,
            BorrowRecord.return_date == None
        ).all()
        
        return render_template('borrow_and_return.html', 
                             available_devices=available_devices,
                             borrowed_devices=borrowed_devices)
    except Exception as e:
        flash(f'发生错误：{str(e)}')
        return redirect(url_for('index'))

@app.route('/apply_borrow/<int:device_id>', methods=['POST'])
def apply_borrow(device_id):
    try:
        device = Device.query.get_or_404(device_id)
        user_id = session.get('user_id', 1)  # 临时使用测试用户ID

        # 检查设备是否可借用
        if device.can_borrow != 1 or device.status != 1:
            flash('该设备当前不可借用')
            return redirect(url_for('borrow_and_return'))
        
        # 检查用户是否已有未归还的相同设备
        existing_borrow = BorrowRecord.query.filter_by(
            user_id=user_id,
            device_id=device_id,
            return_date=None
        ).first()
        
        if existing_borrow:
            flash('您已借用过此设备且尚未归还')
            return redirect(url_for('borrow_and_return'))
        
        # 创建借用记录
        borrow_record = BorrowRecord(
            user_id=user_id,
            device_id=device_id,
            borrow_date=datetime.now().date(),
            approval_status=1  # 待审批
        )
        db.session.add(borrow_record)
        db.session.commit()

        # 记录操作日志
        log_action(user_id, 1, f'申请借用设备：{device.device_name}')
        
        flash('借用申请已提交，等待审批')
        return redirect(url_for('borrow_and_return'))
    except Exception as e:
        db.session.rollback()
        flash(f'申请借用失败：{str(e)}')
        return redirect(url_for('borrow_and_return'))

@app.route('/return_device/<int:device_id>', methods=['POST'])
def return_device(device_id):
    try:
        user_id = session.get('user_id', 1)  # 临时使用测试用户ID
        borrow_record = BorrowRecord.query.filter_by(
            device_id=device_id,
            user_id=user_id,
            return_date=None
        ).first_or_404()
        
        if borrow_record.approval_status != 2:
            flash('只能归还已获批准的设备')
            return redirect(url_for('borrow_and_return'))
        
        borrow_record.return_date = datetime.now().date()
        
        # 更新设备状态
        device = Device.query.get(device_id)
        device.can_borrow = 1
        
        db.session.commit()
        
        # 记录操作日志
        log_action(user_id, 2, f'归还设备：{device.device_name}')
        
        flash('设备已成功归还')
        return redirect(url_for('borrow_and_return'))
    except Exception as e:
        db.session.rollback()
        flash(f'归还设备失败：{str(e)}')
        return redirect(url_for('borrow_and_return'))

@app.route('/review')
def review():
    try:
        pending_records = db.session.query(
            BorrowRecord, Device, User
        ).join(
            Device, BorrowRecord.device_id == Device.device_id
        ).join(
            User, BorrowRecord.user_id == User.user_id
        ).filter(
            BorrowRecord.approval_status == 1  # 待审批
        ).all()
        
        return render_template('review.html', pending_records=pending_records)
    except Exception as e:
        flash(f'获取待审批记录失败：{str(e)}')
        return redirect(url_for('index'))

@app.route('/approve_request/<int:record_id>', methods=['POST'])
def approve_request(record_id):
    try:
        approval_status = request.form.get('approval_status', type=int)
        comment = request.form.get('comment', '')
        approver_id = session.get('user_id', 1)  # 临时使用测试用户ID
        
        if approval_status not in [2, 3]:
            flash('无效的审批状态')
            return redirect(url_for('review'))
        
        borrow_record = BorrowRecord.query.get_or_404(record_id)
        borrow_record.approval_status = approval_status
        
        # 如果批准借用，更新设备状态
        if approval_status == 2:
            device = Device.query.get(borrow_record.device_id)
            device.can_borrow = 0
        
        approval = ApprovalRecord(
            record_id=record_id,
            approver_id=approver_id,
            approval_date=datetime.now().date(),
            approval_comment=comment
        )
        
        db.session.add(approval)
        db.session.commit()
        
        # 记录操作日志
        action_detail = '批准' if approval_status == 2 else '拒绝'
        log_action(approver_id, 3, f'{action_detail}借用申请：记录ID {record_id}')
        
        flash('审批已完成')
        return redirect(url_for('review'))
    except Exception as e:
        db.session.rollback()
        flash(f'审批失败：{str(e)}')
        return redirect(url_for('review'))

if __name__ == '__main__':
    app.run(debug=True)