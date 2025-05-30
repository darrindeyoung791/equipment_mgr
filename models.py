from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    pswd_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.Integer, nullable=False)  # 1:学生 2:教师 3:管理员
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.Integer, nullable=False)  # 1:男 2:女
    dpt = db.Column(db.String(100))
    title = db.Column(db.String(100))
    status = db.Column(db.Integer, nullable=False, default=1)  # 1:正常 2:毕业 3:离职

    def set_password(self, password):
        self.pswd_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pswd_hash, password)

class Device(db.Model):
    __tablename__ = 'devices'
    device_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_name = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Integer, nullable=False)  # 1:正常 2:需要维修 3:维修中 4:报废
    lab = db.Column(db.String(100), nullable=False)
    can_borrow = db.Column(db.Integer, nullable=False)  # 1:是 0:否

class BorrowRecord(db.Model):
    __tablename__ = 'borrow_records'
    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.device_id'), nullable=False)
    borrow_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date)
    approval_status = db.Column(db.Integer, nullable=False)  # 1:待审批 2:已批准 3:已拒绝

class ApprovalRecord(db.Model):
    __tablename__ = 'approval_records'
    approval_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    record_id = db.Column(db.Integer, db.ForeignKey('borrow_records.record_id'), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    approval_date = db.Column(db.Date, nullable=False)
    approval_comment = db.Column(db.Text)

class Log(db.Model):
    __tablename__ = 'logs'
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    action = db.Column(db.Integer, nullable=False)  # 1:设备更新 2:用户删除等
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.now)