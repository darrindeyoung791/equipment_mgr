from flask import Flask, request, jsonify, render_template
import mysql.connector

app = Flask(__name__)

# 数据库连接配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Lcy030522',
    'database': 'equipment_mgr'
}

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
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # 构建查询条件
        query = "SELECT * FROM devices WHERE 1=1"
        params = []
        if 'device_name' in request.args and request.args['device_name']:
            query += " AND device_name LIKE %s"
            params.append(f"%{request.args['device_name']}%")
        if 'model' in request.args and request.args['model']:
            query += " AND model LIKE %s"
            params.append(f"%{request.args['model']}%")
        if 'status' in request.args and request.args['status']:
            query += " AND status = %s"
            params.append(request.args['status'])
        if 'lab' in request.args and request.args['lab']:
            query += " AND lab LIKE %s"
            params.append(f"%{request.args['lab']}%")

        cursor.execute(query, params)
        devices = cursor.fetchall()
        return jsonify(devices)
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# 添加设备接口
@app.route('/api/devices/add', methods=['POST'])
def add_device():
    try:
        data = request.json
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = """
            INSERT INTO devices (device_name, model, purchase_date, price, status, lab, can_borrow)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['device_name'], data['model'], data['purchase_date'],
            data['price'], data['status'], data['lab'], data['can_borrow']
        ))
        conn.commit()
        return jsonify({'message': '设备添加成功'})
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# 编辑设备接口
@app.route('/api/devices/edit', methods=['PUT'])
def edit_device():
    try:
        data = request.json
        conn = mysql.connector.connect(**db_config)
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
