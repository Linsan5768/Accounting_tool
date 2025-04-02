from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from datetime import datetime
import sys
import os
import socket
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')):
    load_dotenv()

# Get environment variables or use defaults
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')
PORT = int(os.getenv('PORT', 5002))

# 计算当前脚本所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 💡 兼容 PyInstaller 打包后的环境
if getattr(sys, 'frozen', False):  # PyInstaller 运行时
    BASE_DIR = sys._MEIPASS  # 获取 PyInstaller 临时目录

# 💡 确保 `models.py` 可被导入
sys.path.append(BASE_DIR)  # 当前目录
sys.path.append(os.path.join(BASE_DIR, "backend"))  # 适配 backend 目录
sys.path.append(os.path.dirname(BASE_DIR))  # 适配 PyInstaller 运行环境

# 💡 确保 `models.py` 存在并可导入
try:
    import models
except ModuleNotFoundError as e:
    print("❌ 错误: models 模块未找到！")
    print(f"🔍 当前 sys.path: {sys.path}")
    raise e  # 抛出异常，确保我们看到完整错误信息

# 绑定数据库模型
Session = models.Session
Record = models.Record
Category = models.Category
insert_default_categories = models.insert_default_categories

# 确保数据库 `accounting.db` 存在
DB_PATH = os.path.join(BASE_DIR, "accounting.db")
if not os.path.exists(DB_PATH):
    print(f"⚠️ 警告: 未找到数据库文件 {DB_PATH}，将尝试创建...")
    models.init_db()  # 重新初始化数据库

# 计算 Vue 前端路径
DIST_DIR = os.path.join(BASE_DIR, "web_frontend/dist")
if not os.path.exists(DIST_DIR):  # 兼容 PyInstaller 打包后路径
    DIST_DIR = os.path.join(BASE_DIR, "../web_frontend/dist")

app = Flask(__name__, static_folder=DIST_DIR, static_url_path="/")

# Configure CORS based on environment
if DEBUG:
    # In development, allow all origins for easier testing
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
else:
    # In production, restrict origins for security
    allowed_origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')
    CORS(app, resources={r"/*": {"origins": allowed_origins}}, supports_credentials=True)

# ===== 记账 API =====
@app.route('/api/add_record', methods=['POST'])
def add_record():
    """添加记账记录"""
    data = request.json
    s = Session()
    try:
        record = Record(
            date=datetime.strptime(data.get('date'), '%Y-%m-%d'),
            amount=data.get('amount'),
            category_id=data.get('category_id'),
            remarks=data.get('remarks')
        )
        s.add(record)
        s.commit()
        return jsonify({'message': '记录添加成功'}), 200
    except Exception as e:
        s.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        s.close()

@app.route('/api/get_records', methods=['GET'])
def get_records():
    """获取所有记账记录"""
    s = Session()
    try:
        from sqlalchemy.orm import joinedload
        records = s.query(Record).options(joinedload(Record.category)).all()
        result = [{
            'id': r.id,
            'date': r.date.strftime('%Y-%m-%d'),
            'amount': r.amount,
            'category_id': r.category_id,
            'category': r.category.name if r.category else '',
            'remarks': r.remarks
        } for r in records]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        s.close()

@app.route('/api/delete_record/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    """删除一条记账记录"""
    s = Session()
    try:
        print(f"🔍 尝试删除记录 ID: {record_id}")  # ✅ 添加调试信息

        record = s.query(Record).filter_by(id=record_id).first()
        if not record:
            print(f"❌ 记录 {record_id} 不存在！")  # ✅ 添加调试信息
            return jsonify({'error': '记录不存在'}), 404
        
        s.delete(record)
        s.commit()
        print(f"✅ 记录 {record_id} 删除成功！")  # ✅ 添加调试信息
        return jsonify({'message': '记录删除成功'}), 200
    except Exception as e:
        s.rollback()
        print(f"❌ 删除失败: {e}")  # ✅ 添加调试信息
        return jsonify({'error': str(e)}), 400
    finally:
        s.close()

@app.route('/api/update_record/<int:record_id>', methods=['PUT'])
def update_record(record_id):
    data = request.json
    s = Session()
    try:
        print(f"🔍 接收到更新请求，记录ID: {record_id}, 数据: {data}")
        
        record = s.query(Record).filter_by(id=record_id).first()
        if not record:
            print(f"❌ 记录 {record_id} 不存在！")
            return jsonify({'error': '记录不存在'}), 404
            
        # 处理日期
        if 'date' in data:
            try:
                record.date = datetime.strptime(data.get('date'), '%Y-%m-%d')
                print(f"✅ 日期更新为: {record.date}")
            except ValueError as e:
                print(f"❌ 日期格式错误: {e}")
                return jsonify({'error': f'日期格式错误: {e}'}), 400
            
        # 处理金额
        if 'amount' in data:
            try:
                record.amount = float(data.get('amount'))
                print(f"✅ 金额更新为: {record.amount}")
            except ValueError as e:
                print(f"❌ 金额格式错误: {e}")
                return jsonify({'error': f'金额格式错误: {e}'}), 400
            
        # 处理类别ID
        if 'category_id' in data and data['category_id'] is not None:
            record.category_id = data.get('category_id')
            print(f"✅ 类别ID更新为: {record.category_id}")
        # 如果前端传递了类别名称，通过名称查找对应的ID
        elif 'category' in data and data['category']:
            try:
                category = s.query(Category).filter_by(name=data['category']).first()
                if category:
                    record.category_id = category.id
                    print(f"✅ 通过名称 '{data['category']}' 找到类别ID: {category.id}")
                else:
                    # 如果类别不存在，则创建新类别
                    new_category = Category(name=data['category'])
                    s.add(new_category)
                    s.flush()  # 获取新类别的ID
                    record.category_id = new_category.id
                    print(f"✅ 创建新类别 '{data['category']}', ID: {new_category.id}")
            except Exception as e:
                print(f"❌ 处理类别时出错: {e}")
                return jsonify({'error': f'处理类别时出错: {e}'}), 400
                
        # 处理备注
        if 'remarks' in data:
            record.remarks = data.get('remarks')
            print(f"✅ 备注更新为: {record.remarks}")
            
        s.commit()
        print(f"✅ 记录 {record_id} 更新成功!")
        return jsonify({'message': '记录更新成功', 'record_id': record_id}), 200
    except Exception as e:
        s.rollback()
        print(f"❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()  # 打印详细错误堆栈
        return jsonify({'error': str(e)}), 400
    finally:
        s.close()

@app.route('/api/get_categories', methods=['GET'])
def get_categories():
    """获取所有类别"""
    s = Session()
    try:
        categories = s.query(Category).all()
        result = [{'id': cat.id, 'name': cat.name} for cat in categories]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        s.close()

# ===== Vue 前端托管 =====
@app.route("/")
def serve_vue():
    """返回 Vue 前端的 index.html"""
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    """返回 Vue 其他静态文件（JS、CSS、图片等）"""
    return send_from_directory(app.static_folder, path)

# ===== 端口占用检查 =====
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

if __name__ == '__main__':
    if is_port_in_use(PORT):
        print(f"⚠️  端口 {PORT} 已被占用，请先释放端口或使用其他端口！")
        sys.exit(1)

    print(f"✅ Running Flask on port {PORT}, Debug mode: {DEBUG}")
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG, use_reloader=False)