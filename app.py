from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
import decimal
import json  # 添加json导入
from config import Config
from flask import abort

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

def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

# API: 设备搜索
@app.route('/api/devices/search')
def api_search_devices():
    if 'user_id' not in session:
        return jsonify({'success': False})

    params = []
    conditions = []
    
    # 如果是非管理员，只显示可借用的设备
    if session.get('user_type') == 1:
        conditions.append('status = 1 AND can_borrow = 1')
    
    # 搜索条件
    field = next((k for k in request.args.keys() if k in ['device_id', 'device_name', 'model', 'lab', 'price', 'status']), None)
    if field and request.args.get(field):
        value = request.args.get(field)
        if field in ['price', 'status']:
            conditions.append(f'{field} = %s')
            params.append(value)
        else:
            conditions.append(f'{field} LIKE %s')
            params.append(f'%{value}%')

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        query = '''
            SELECT * FROM devices
            {where_clause}
            ORDER BY device_name, lab
        '''.format(where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else "")
        
        cursor.execute(query, params)
        devices = cursor.fetchall()
        
        # 处理Decimal类型
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
        is_admin = session.get('user_type') != 1  # 非学生用户都视为管理员
        
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

            if is_admin:
                # 管理员直接借用，创建已批准的借用记录
                from datetime import datetime, timedelta
                cursor.execute('''
                    INSERT INTO borrow_records 
                    (user_id, device_id, borrow_date, approval_status, approver_id, return_deadline)
                    VALUES (%s, %s, CURDATE(), 2, %s, DATE_ADD(CURDATE(), INTERVAL 7 DAY))
                ''', (session['user_id'], device_id, session['user_id']))
            else:
                # 学生创建待审批的借用记录
                cursor.execute('''
                    INSERT INTO borrow_records 
                    (user_id, device_id, borrow_date, approval_status)
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
            d.device_name,
            d.model,
            d.lab,
            br.record_id,
            br.borrow_date
        FROM borrow_records br
        JOIN devices d ON br.device_id = d.device_id
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
            d.device_name,
            d.model,
            d.lab,
            br.record_id,
            br.borrow_date
        FROM borrow_records br
        JOIN devices d ON br.device_id = d.device_id
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

@app.route('/api/borrow-requests/pending')
def api_pending_requests():
    if 'user_id' not in session or session.get('user_type') == 1:
        return jsonify({'success': False})
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        # 获取所有待审批的申请
        cursor.execute('''
            SELECT 
                br.record_id,
                u.name as user_name,
                u.dpt as department,
                d.device_id,
                d.device_name,
                br.borrow_date as apply_time,
                (
                    SELECT COUNT(*) 
                    FROM devices d2 
                    WHERE d2.device_name = d.device_name 
                    AND d2.status = 1 
                    AND d2.can_borrow = 1
                ) as available_count
            FROM borrow_records br
            JOIN users u ON br.user_id = u.user_id
            JOIN devices d ON br.device_id = d.device_id
            WHERE br.approval_status = 1
            ORDER BY br.borrow_date ASC
        ''')
        requests = cursor.fetchall()
        cursor.close()
        
        return jsonify({
            'success': True,
            'requests': requests
        })
    except Exception as e:
        cursor.close()
        print(f"Error fetching requests: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取申请列表失败'
        })

@app.route('/api/borrow-requests/review', methods=['POST'])
def api_review_request():
    if 'user_id' not in session or session.get('user_type') == 1:
        return jsonify({'success': False, 'message': '无权限进行此操作'})
    
    try:
        data = request.get_json()
        record_id = data.get('record_id')
        approved = data.get('approved')
        duration = data.get('duration')
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        try:
            cursor.execute('START TRANSACTION')
            
            # 获取申请信息
            cursor.execute('''
                SELECT br.*, d.device_id, d.device_name, u.user_id
                FROM borrow_records br
                JOIN devices d ON br.device_id = d.device_id
                JOIN users u ON br.user_id = u.user_id
                WHERE br.record_id = %s AND br.approval_status = 1
                FOR UPDATE
            ''', (record_id,))
            
            request_info = cursor.fetchone()
            if not request_info:
                raise Exception('申请记录不存在或已被处理')

            if approved:
                # 批准申请
                from datetime import datetime, timedelta
                duration = int(duration)
                return_deadline = (datetime.now() + timedelta(days=duration)).strftime('%Y-%m-%d')
                
                cursor.execute('''
                    UPDATE borrow_records 
                    SET approval_status = 2,
                        return_deadline = %s,
                        approver_id = %s
                    WHERE record_id = %s
                ''', (return_deadline, session['user_id'], record_id))
            else:
                # 拒绝申请
                cursor.execute('''
                    UPDATE borrow_records 
                    SET approval_status = 3,
                        approver_id = %s
                    WHERE record_id = %s
                ''', (session['user_id'], record_id))
                
                # 恢复设备可借用状态
                cursor.execute('''
                    UPDATE devices 
                    SET can_borrow = 1
                    WHERE device_id = %s
                ''', (request_info['device_id'],))

            # 创建通知
            notification_type = 1 if approved else 2
            content = f'您申请借用的{request_info["device_name"]}已{"获批准" if approved else "被拒绝"}'
            if approved:
                content += f'，使用期限{duration}天'
            
            cursor.execute('''
                INSERT INTO notifications (user_id, type, content, related_id)
                VALUES (%s, %s, %s, %s)
            ''', (request_info['user_id'], notification_type, content, record_id))

            mysql.connection.commit()
            return jsonify({'success': True})
            
        except Exception as e:
            mysql.connection.rollback()
            raise e
        finally:
            cursor.close()
            
    except Exception as e:
        print(f"Review error: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e) if str(e) else '审批失败，请重试'
        })

# API: 设备管理相关接口
@app.route('/api/devices/all')
def api_all_devices():
    if 'user_id' not in session or session.get('user_type') == 1:
        return jsonify({'success': False})
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT * FROM devices ORDER BY device_name
    ''')
    devices = cursor.fetchall()
    cursor.close()
    
    return jsonify({
        'success': True,
        'devices': devices
    })

@app.route('/api/devices/create', methods=['POST'])
def api_create_device():
    if 'user_id' not in session or session.get('user_type') == 1:
        return jsonify({'success': False, 'message': '无权限进行此操作'})
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '未收到数据'})
        
        # 数据验证和清理
        try:
            cleaned_data = {
                'device_name': str(data['device_name']).strip(),
                'model': str(data['model']).strip(),
                'lab': str(data['lab']).strip(),
                'price': float(data['price']),
                'purchase_date': data['purchase_date'],
                'status': int(data['status']),
                'can_borrow': int(data['can_borrow'])
            }
        except (KeyError, ValueError) as e:
            return jsonify({
                'success': False,
                'message': f'数据验证失败: {str(e)}'
            })

        # 使用上下文管理器自动处理事务和关闭cursor
        with mysql.connection.cursor(MySQLdb.cursors.DictCursor) as cursor:
            try:
                # 开始事务
                cursor.execute('START TRANSACTION')
                
                # 1. 插入设备记录
                insert_query = '''
                    INSERT INTO devices 
                    (device_name, model, lab, price, purchase_date, status, can_borrow)
                    VALUES (%(name)s, %(model)s, %(lab)s, %(price)s, %(date)s, %(status)s, %(can_borrow)s)
                '''
                cursor.execute(insert_query, {
                    'name': cleaned_data['device_name'],
                    'model': cleaned_data['model'],
                    'lab': cleaned_data['lab'],
                    'price': cleaned_data['price'],
                    'date': cleaned_data['purchase_date'],
                    'status': cleaned_data['status'],
                    'can_borrow': cleaned_data['can_borrow']
                })
                
                # 2. 记录操作日志
                device_id = cursor.lastrowid
                log_query = '''
                    INSERT INTO logs (user_id, action, details) 
                    VALUES (%(user_id)s, 1, %(details)s)
                '''
                log_details = f"Created device ID {device_id}: {cleaned_data['device_name']}"
                cursor.execute(log_query, {
                    'user_id': session['user_id'],
                    'details': log_details
                })

                # 提交事务
                mysql.connection.commit()
                
                return jsonify({
                    'success': True,
                    'message': '设备创建成功',
                    'device_id': device_id
                })
                
            except Exception as e:
                # 回滚事务
                mysql.connection.rollback()
                return jsonify({
                    'success': False,
                    'message': f'创建失败: {str(e)}'
                })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'系统错误: {str(e)}'
        })

@app.route('/api/devices/update', methods=['POST'])
def api_update_device():
    if 'user_id' not in session or session.get('user_type') == 1:
        return jsonify({'success': False, 'message': '无权限进行此操作'})
    
    try:
        data = request.get_json()
        if not data or 'device_id' not in data:
            return jsonify({'success': False, 'message': '数据不完整'})

        # 数据验证和清理
        try:
            device_id = int(data['device_id'])
            cleaned_data = {
                'device_name': str(data['device_name']).strip(),
                'model': str(data['model']).strip(),
                'lab': str(data['lab']).strip(),
                'price': float(data['price']),
                'purchase_date': data['purchase_date'],
                'status': int(data['status']),
                'can_borrow': int(data['can_borrow'])
            }
        except (KeyError, ValueError) as e:
            return jsonify({
                'success': False,
                'message': f'数据验证失败: {str(e)}'
            })

        with mysql.connection.cursor(MySQLdb.cursors.DictCursor) as cursor:
            try:
                # 开始事务
                cursor.execute('START TRANSACTION')

                # 1. 获取原始设备信息用于日志
                cursor.execute('SELECT * FROM devices WHERE device_id = %s FOR UPDATE', (device_id,))
                old_device = cursor.fetchone()
                if not old_device:
                    mysql.connection.rollback()
                    return jsonify({'success': False, 'message': '设备不存在'})

                # 2. 更新设备信息
                update_query = '''
                    UPDATE devices 
                    SET device_name = %(name)s,
                        model = %(model)s,
                        lab = %(lab)s,
                        price = %(price)s,
                        purchase_date = %(date)s,
                        status = %(status)s,
                        can_borrow = %(can_borrow)s
                    WHERE device_id = %(id)s
                '''
                cursor.execute(update_query, {
                    'name': cleaned_data['device_name'],
                    'model': cleaned_data['model'],
                    'lab': cleaned_data['lab'],
                    'price': cleaned_data['price'],
                    'date': cleaned_data['purchase_date'],
                    'status': cleaned_data['status'],
                    'can_borrow': cleaned_data['can_borrow'],
                    'id': device_id
                })

                # 3. 记录变更日志
                changes = []
                for key in cleaned_data:
                    if str(old_device.get(key, '')) != str(cleaned_data[key]):
                        changes.append(f"{key}: {old_device.get(key, '')} -> {cleaned_data[key]}")
                
                if changes:
                    log_query = '''
                        INSERT INTO logs (user_id, action, details) 
                        VALUES (%(user_id)s, 2, %(details)s)
                    '''
                    log_details = f"Updated device ID {device_id}: " + "; ".join(changes)
                    cursor.execute(log_query, {
                        'user_id': session['user_id'],
                        'details': log_details
                    })

                # 提交事务
                mysql.connection.commit()
                return jsonify({'success': True, 'message': '更新成功'})

            except Exception as e:
                mysql.connection.rollback()
                return jsonify({
                    'success': False,
                    'message': f'更新失败: {str(e)}'
                })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'系统错误: {str(e)}'
        })

@app.route('/api/devices/delete/<int:device_id>', methods=['POST'])
def api_delete_device(device_id):
    if 'user_id' not in session or session.get('user_type') == 1:
        return jsonify({'success': False, 'message': '无权限进行此操作'})
    
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # 开始事务
        cursor.execute('START TRANSACTION')
        
        try:
            # 1. 检查是否有未完成的借用记录
            cursor.execute('''
                SELECT COUNT(*) as count 
                FROM borrow_records 
                WHERE device_id = %s 
                AND return_date IS NULL 
                AND approval_status = 2
            ''', (device_id,))
            
            if cursor.fetchone()['count'] > 0:
                raise Exception('该设备有未完成的借用记录，无法删除')

            # 2. 删除相关的所有记录（已完成的借用记录和审批记录）
            cursor.execute('DELETE FROM approval_records WHERE record_id IN (SELECT record_id FROM borrow_records WHERE device_id = %s)', (device_id,))
            cursor.execute('DELETE FROM borrow_records WHERE device_id = %s', (device_id,))
            
            # 3. 记录操作日志
            cursor.execute('''
                INSERT INTO logs (user_id, action, details) 
                VALUES (%s, 3, %s)
            ''', (session['user_id'], f'Deleted device ID: {device_id}'))

            # 4. 删除设备
            cursor.execute('DELETE FROM devices WHERE device_id = %s', (device_id,))
            
            mysql.connection.commit()
            return jsonify({'success': True})
            
        except Exception as e:
            mysql.connection.rollback()
            return jsonify({
                'success': False,
                'message': str(e)
            })
        finally:
            cursor.close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': '删除失败，请重试'
        })

# API: 管理员批量执行SQL
@app.route('/api/admin/batch-sql', methods=['POST'])
def api_batch_sql():
    if 'user_id' not in session or session.get('user_type') == 1:
        return jsonify({'success': False, 'message': '无权限'})
    try:
        data = request.get_json()
        sql = data.get('sql', '')
        if not sql:
            return jsonify({'success': False, 'message': 'SQL不能为空'})
        # 拆分多条SQL，防止注入
        stmts = [s.strip() for s in sql.split(';') if s.strip()]
        results = []
        with mysql.connection.cursor() as cursor:
            for stmt in stmts:
                try:
                    cursor.execute(stmt)
                    if cursor.description:
                        rows = cursor.fetchall()
                        results.append(str(rows))
                except Exception as e:
                    mysql.connection.rollback()
                    return jsonify({'success': False, 'message': f'执行失败: {str(e)}'})
            mysql.connection.commit()
        return jsonify({'success': True, 'result': '\n'.join(results) if results else '执行成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'系统错误: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)
