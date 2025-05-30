from flask import Flask, request, jsonify, render_template
import mysql.connector
from mysql.connector import pooling
import signal
import sys

app = Flask(__name__)

# 确保 JSON 数据支持中文
app.config['JSON_AS_ASCII'] = False

# 数据库连接池配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Lcy030522',
    'database': 'equipment_mgr',
    'pool_name': 'mypool',
    'pool_size': 5
}

# 创建连接池
connection_pool = mysql.connector.pooling.MySQLConnectionPool(**db_config)

# 捕获应用程序终止信号
def handle_exit_signal(signal, frame):
    print("Application is shutting down. Closing database connections...")
    connection_pool.close()  # 关闭连接池
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit_signal)
signal.signal(signal.SIGTERM, handle_exit_signal)

# 首页路由
@app.route('/')
def index():
    return render_template('index.html')  # 渲染 index.html

# 渲染设备查询页面
@app.route('/query')
def query_page():
    return render_template('query.html')

# 渲染设备录入与编辑页面
@app.route('/devices')
def devices_page():
    return render_template('devices.html')

# 查询设备接口
@app.route('/api/devices/query', methods=['GET'])
def query_devices():
    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        # 构建查询条件
        query = "SELECT * FROM devices"
        conditions = []
        params = []
        if 'device_name' in request.args and request.args['device_name']:
            device_name = request.args['device_name']
            print("Received device_name:", device_name)  # 调试日志
            conditions.append("device_name LIKE %s")
            params.append(f"%{device_name}%")
        if 'model' in request.args and request.args['model']:
            conditions.append("model LIKE %s")
            params.append(f"%{request.args['model']}%")
        if 'status' in request.args and request.args['status']:
            conditions.append("status = %s")
            params.append(request.args['status'])
        if 'lab' in request.args and request.args['lab']:
            conditions.append("lab LIKE %s")
            params.append(f"%{request.args['lab']}%")

        # 拼接查询条件
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        print("Executing query:", query, "with params:", params)  # 调试日志
        cursor.execute(query, params)
        devices = cursor.fetchall()
        print("Query results:", devices)  # 调试日志
        return jsonify(devices)
    except mysql.connector.Error as err:
        print("Database error:", err)  # 调试日志
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# 添加设备接口
@app.route('/api/devices/add', methods=['POST'])
def add_device():
    try:
        data = request.json
        print("Received data for adding device:", data)  # 调试日志

        # 验证字段
        required_fields = ['device_name', 'model', 'purchase_date', 'price', 'status', 'lab', 'can_borrow']
        for field in required_fields:
            if field not in data:
                print(f"Missing field: {field}")  # 调试日志
                return jsonify({'error': f'Missing field: {field}'}), 400

        # 验证数据格式
        try:
            data['price'] = float(data['price'])
            data['status'] = int(data['status'])
            data['can_borrow'] = int(data['can_borrow'])
        except ValueError as e:
            print("Invalid data format:", e)  # 调试日志
            return jsonify({'error': 'Invalid data format'}), 400

        conn = connection_pool.get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO devices (device_name, model, purchase_date, price, status, lab, can_borrow)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        print("Executing query:", query)  # 调试日志
        print("With parameters:", (
            data['device_name'], data['model'], data['purchase_date'],
            data['price'], data['status'], data['lab'], data['can_borrow']
        ))  # 调试日志

        cursor.execute(query, (
            data['device_name'], data['model'], data['purchase_date'],
            data['price'], data['status'], data['lab'], data['can_borrow']
        ))
        conn.commit()
        print("Device added successfully.")  # 调试日志
        return jsonify({'message': '设备添加成功'})
    except mysql.connector.Error as err:
        print("Database error:", err)  # 调试日志
        return jsonify({'error': str(err)}), 500
    except Exception as e:
        print("Unexpected error:", e)  # 调试日志
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# 编辑设备接口
@app.route('/api/devices/edit', methods=['PUT'])
def edit_device():
    try:
        data = request.json
        conn = connection_pool.get_connection()
        cursor = conn.cursor()

        query = """
            UPDATE devices
            SET device_name = %s, model = %s, purchase_date = %s, price = %s,
                status = %s, lab = %s, can_borrow = %s
            WHERE device_id = %s
        """
        cursor.execute(query, (
            data['device_name'], data['model'], data['purchase_date'],
            data['price'], data['status'], data['lab'], data['can_borrow'],
            data['device_id']
        ))
        conn.commit()
        return jsonify({'message': '设备信息更新成功'})
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
