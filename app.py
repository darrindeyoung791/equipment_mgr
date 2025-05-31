from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
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

if __name__ == '__main__':
    app.run(debug=True)
