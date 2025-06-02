from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
import decimal  # 添加这一行
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
mysql = MySQL(app)

# 根路由重定向到登录页
@app.route('/')
def root():
    return redirect(url_for('login'))

# 登录页路由
@app.route('/login')
def login():
    return render_template('login.html')

# 注册页路由
@app.route('/register')
def register():
    return render_template('sign_up.html')

# 首页路由
@app.route('/index')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

# 通知页路由
@app.route('/notifications')
def notifications():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('notifications.html')

# 设备管理页路由
@app.route('/edit_devices')
def edit_devices():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('user_type') == 1:  # 学生
        return redirect(url_for('index'))
    return render_template('edit_devices.html')

# 借用申请页路由
@app.route('/borrow')
def borrow():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('borrow.html')

# 归还页路由
@app.route('/return')
def return_equipment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('return.html')

# 申请审核页路由
@app.route('/review')
def review():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('user_type') == 1:  # 学生
        return redirect(url_for('index'))
    return render_template('review.html')

# API: 登录验证
@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        username = data.get('username')
        password_hash = data.get('password')

        # 调试信息
        print(f"Debug - Login attempt for user: {username}")
        print(f"Debug - Received password hash: {password_hash}")

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # 首先检查用户是否存在
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            })

        # 调试信息
        print(f"Debug - Stored password hash: {user['pswd_hash']}")
        print(f"Debug - Hash comparison: {password_hash == user['pswd_hash']}")

        # 验证密码哈希
        if password_hash == user['pswd_hash'] and user['status'] == 1:
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['user_type'] = user['user_type']
            cursor.close()
            return jsonify({'success': True})
        
        cursor.close()
        return jsonify({
            'success': False,
            'message': '用户名或密码错误'
        })
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'message': '登录失败，请重试'
        })

# API: 注册用户
@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json()
        username = data.get('username')
        name = data.get('name')
        gender = data.get('gender')
        department = data.get('department')
        password_hash = data.get('password')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # 检查用户名是否已存在
        cursor.execute('SELECT user_id FROM users WHERE username = %s', (username,))
        if cursor.fetchone():
            cursor.close()
            return jsonify({
                'success': False,
                'message': '用户名已存在'
            })

        # 插入新用户，包含所有必填字段
        cursor.execute('''
            INSERT INTO users (username, name, gender, dpt, title, pswd_hash, user_type, status) 
            VALUES (%s, %s, %s, %s, '无', %s, 1, 1)
        ''', (username, name, gender, department, password_hash))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'success': True})
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({
            'success': False,
            'message': '注册失败，请重试'
        })

@app.route('/api/user-info')
def api_user_info():
    if 'user_id' not in session:
        return jsonify({'success': False})
    return jsonify({
        'success': True,
        'username': session.get('username'),
        'user_type': session.get('user_type')
    })

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/notifications')
def api_notifications():
    if 'user_id' not in session:
        return jsonify({'success': False})
        
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT * FROM notifications 
        WHERE user_id = %s 
        ORDER BY created_at DESC
    ''', (session['user_id'],))
    
    notifications = cursor.fetchall()
    cursor.close()
    
    return jsonify({
        'success': True,
        'notifications': notifications
    })

@app.route('/api/notifications/mark-all-read', methods=['POST'])
def api_mark_all_read():
    if 'user_id' not in session:
        return jsonify({'success': False})
        
    cursor = mysql.connection.cursor()
    cursor.execute('''
        UPDATE notifications 
        SET read_status = 1 
        WHERE user_id = %s
    ''', (session['user_id'],))
    
    mysql.connection.commit()
    cursor.close()
    
    return jsonify({'success': True})

@app.route('/api/notifications/mark-read/<int:notification_id>', methods=['POST'])
def api_mark_notification_read(notification_id):
    if 'user_id' not in session:
        return jsonify({'success': False})
        
    cursor = mysql.connection.cursor()
    cursor.execute('''
        UPDATE notifications 
        SET read_status = 1 
        WHERE notification_id = %s AND user_id = %s
    ''', (notification_id, session['user_id']))
    
    mysql.connection.commit()
    cursor.close()
    
    return jsonify({'success': True})

# API: 获取可用的实验室列表
@app.route('/api/labs')
def api_labs():
    if 'user_id' not in session:
        return jsonify({'success': False})
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT DISTINCT lab FROM devices WHERE status = 1 AND can_borrow = 1')
    labs = [row['lab'] for row in cursor.fetchall()]
    cursor.close()
    
    return jsonify({
        'success': True,
        'values': labs
    })

# API: 设备名称列表
@app.route('/api/devices/names')
def api_device_names():
    if 'user_id' not in session:
        return jsonify({'success': False})
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT DISTINCT device_name FROM devices WHERE status = 1 AND can_borrow = 1')
    names = [row['device_name'] for row in cursor.fetchall()]
    cursor.close()
    
    return jsonify({
        'success': True,
        'values': names
    })

# API: 设备型号列表
@app.route('/api/devices/models')
def api_device_models():
    if 'user_id' not in session:
        return jsonify({'success': False})
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT DISTINCT model FROM devices WHERE status = 1 AND can_borrow = 1')
    models = [row['model'] for row in cursor.fetchall()]
    cursor.close()
    
    return jsonify({
        'success': True,
        'values': models
    })

# API: 设备类型列表
@app.route('/api/devices/types')
def api_device_types():
    if 'user_id' not in session:
        return jsonify({'success': False})
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT DISTINCT dt.type_name 
        FROM device_types dt 
        JOIN devices d ON dt.type_id = d.type_id 
        WHERE d.status = 1 AND d.can_borrow = 1
    ''')
    types = [row['type_name'] for row in cursor.fetchall()]
    cursor.close()
    
    return jsonify({
        'success': True,
        'values': types
    })

# API: 设备搜索
@app.route('/api/devices/search')
def api_search_devices():
    if 'user_id' not in session:
        return jsonify({'success': False})

    params = []
    conditions = []
    
    # 基础条件：只显示可借用的设备
    conditions.append('d.status = 1 AND d.can_borrow = 1')
    
    # 搜索条件
    field = next((k for k in request.args.keys() if k in ['type_name', 'model', 'lab']), None)
    if field and request.args.get(field):
        value = request.args.get(field)
        if field == 'type_name':
            conditions.append('dt.type_name LIKE %s')
        elif field == 'model':
            conditions.append('dt.model LIKE %s')
        elif field == 'lab':
            conditions.append('d.lab LIKE %s')
        params.append(f'%{value}%')

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = f'''
            SELECT DISTINCT
                d.device_id,
                dt.type_name as device_name,
                dt.model,
                d.lab,
                d.purchase_date,
                d.price,
                d.status,
                d.can_borrow
            FROM devices d
            JOIN device_types dt ON d.type_id = dt.type_id
            WHERE {' AND '.join(conditions)}
            ORDER BY dt.type_name, d.lab
        '''
        
        cursor.execute(query, params)
        devices = cursor.fetchall()
        
        # 转换 Decimal 为 float
        for device in devices:
            if 'price' in device and isinstance(device['price'], decimal.Decimal):
                device['price'] = float(device['price'])
        
        cursor.close()
        
        return jsonify({
            'success': True,
            'devices': devices
        })
    except Exception as e:
        print(f"Search error: {str(e)}")
        return jsonify({
            'success': False,
            'message': '搜索失败，请重试'
        })

# API: 提交借用申请
@app.route('/api/borrow-request', methods=['POST'])
def api_borrow_request():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})

    try:
        data = request.get_json()
        device_id = data.get('device_id')
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # 检查设备是否可借
        cursor.execute('''
            SELECT device_id, device_name
            FROM devices 
            WHERE device_id = %s AND status = 1 AND can_borrow = 1
        ''', (device_id,))
        device = cursor.fetchone()
        
        if not device:
            cursor.close()
            return jsonify({'success': False, 'message': '设备不可借用'})

        # 开始事务
        cursor.execute('START TRANSACTION')
        
        try:
            # 更新设备状态为不可借用
            cursor.execute('''
                UPDATE devices 
                SET can_borrow = 0
                WHERE device_id = %s
            ''', (device_id,))

            # 创建借用记录
            cursor.execute('''
                INSERT INTO borrow_records (user_id, device_id, borrow_date, approval_status)
                VALUES (%s, %s, CURDATE(), 1)
            ''', (session['user_id'], device_id))
            record_id = cursor.lastrowid

            # 为管理员创建通知
            cursor.execute('SELECT user_id FROM users WHERE user_type IN (2, 3)')
            admins = cursor.fetchall()
            
            for admin in admins:
                cursor.execute('''
                    INSERT INTO notifications 
                    (user_id, type, content, related_id)
                    VALUES (%s, 1, %s, %s)
                ''', (
                    admin['user_id'],
                    f'新的借用申请：{device["device_name"]}',
                    record_id
                ))

            mysql.connection.commit()
            cursor.close()
            return jsonify({'success': True})
            
        except Exception as e:
            mysql.connection.rollback()
            cursor.close()
            return jsonify({'success': False, 'message': '申请提交失败，请重试'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': '申请提交失败，请重试'})

@app.route('/api/devices/borrowed')
def api_borrowed_devices():
    if 'user_id' not in session:
        return jsonify({'success': False})
        
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT 
            d.device_id,
            dt.type_name as device_name,
            dt.model,
            d.lab,
            br.record_id,
            br.borrow_date
        FROM borrow_records br
        JOIN devices d ON br.device_id = d.device_id
        JOIN device_types dt ON d.type_id = dt.type_id
        WHERE br.user_id = %s
        AND br.approval_status = 2
        AND br.return_date IS NULL
        ORDER BY br.borrow_date DESC
    ''', (session['user_id'],))
    
    devices = cursor.fetchall()
    cursor.close()
    
    return jsonify({
        'success': True,
        'devices': devices
    })

@app.route('/api/devices/pending')
def api_pending_devices():
    if 'user_id' not in session:
        return jsonify({'success': False})
        
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT 
            d.device_id,
            dt.type_name as device_name,
            dt.model,
            d.lab,
            br.record_id,
            br.borrow_date
        FROM borrow_records br
        JOIN devices d ON br.device_id = d.device_id
        JOIN device_types dt ON d.type_id = dt.type_id
        WHERE br.user_id = %s
        AND br.approval_status = 1
        ORDER BY br.borrow_date DESC
    ''', (session['user_id'],))
    
    devices = cursor.fetchall()
    cursor.close()
    
    return jsonify({
        'success': True,
        'devices': devices
    })

@app.route('/api/return-device', methods=['POST'])
def api_return_device():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})

    try:
        data = request.get_json()
        record_id = data.get('record_id')
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # 开始事务
        cursor.execute('START TRANSACTION')
        
        try:
            # 更新借用记录
            cursor.execute('''
                UPDATE borrow_records 
                SET return_date = CURDATE()
                WHERE record_id = %s AND user_id = %s
            ''', (record_id, session['user_id']))

            # 获取设备ID
            cursor.execute('SELECT device_id FROM borrow_records WHERE record_id = %s', (record_id,))
            device = cursor.fetchone()

            # 更新设备状态
            cursor.execute('''
                UPDATE devices 
                SET can_borrow = 1
                WHERE device_id = %s
            ''', (device['device_id'],))

            mysql.connection.commit()
            cursor.close()
            return jsonify({'success': True})
            
        except Exception as e:
            mysql.connection.rollback()
            cursor.close()
            return jsonify({'success': False, 'message': '归还失败，请重试'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': '归还失败，请重试'})

@app.route('/api/cancel-request', methods=['POST'])
def api_cancel_request():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})

    try:
        data = request.get_json()
        record_id = data.get('record_id')
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # 开始事务
        cursor.execute('START TRANSACTION')
        
        try:
            # 获取设备ID
            cursor.execute('SELECT device_id FROM borrow_records WHERE record_id = %s', (record_id,))
            device = cursor.fetchone()

            # 删除借用记录
            cursor.execute('''
                DELETE FROM borrow_records 
                WHERE record_id = %s AND user_id = %s AND approval_status = 1
            ''', (record_id, session['user_id']))

            # 更新设备状态
            cursor.execute('''
                UPDATE devices 
                SET can_borrow = 1
                WHERE device_id = %s
            ''', (device['device_id'],))

            mysql.connection.commit()
            cursor.close()
            return jsonify({'success': True})
            
        except Exception as e:
            mysql.connection.rollback()
            cursor.close()
            return jsonify({'success': False, 'message': '取消失败，请重试'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': '取消失败，请重试'})

if __name__ == '__main__':
    app.run(debug=True)
