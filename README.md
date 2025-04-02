# 记账工具 (Accounting Tool)

一个简单易用的本地记账工具，包含 Vue 前端和 Flask 后端，支持添加、编辑、删除记账记录，并提供基础的图表统计和分类功能。

---

## 🧩 项目结构

```
accounting_tool/
├── backend/          # Flask 后端
│   ├── app.py        # 主应用入口
│   ├── models.py     # 数据库模型定义
│   └── requirements.txt
├── web_frontend/     # Vue 前端
│   ├── src/
│   ├── public/
│   └── package.json
└── accounting.db     # SQLite 本地数据库（运行后自动生成）
```

---

## 🖥️ 本地运行指南

### ✅ 后端（Flask）

1. 打开终端，进入 `backend` 目录：

```bash
cd backend
```

2. 创建并激活虚拟环境（推荐）：

```bash
python3 -m venv venv
source venv/bin/activate
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

4. 启动服务：

```bash
python app.py
```

> 默认监听在 `http://localhost:5002`

---

### ✅ 前端（Vue 3 + Vue CLI）

1. 打开另一个终端，进入 `web_frontend`：

```bash
cd web_frontend
```

2. 安装依赖：

```bash
npm install
```

3. 启动开发服务器：

```bash
npm run serve
```

> 默认监听在 `http://localhost:8080`

---

## 🌐 使用方式

- 前端访问：打开浏览器访问 [http://localhost:8080](http://localhost:8080)
- 前端会通过接口连接本地后端（需确保接口地址为 `http://localhost:5002`）

---

## 🛠️ 技术栈

- 前端：Vue.js, Chart.js, Bootstrap, Axios
- 后端：Flask, SQLAlchemy, SQLite
- 其他：dotenv, flask-cors, gunicorn（用于部署）

---

## 📝 说明

- 默认数据库为 `SQLite`，运行时自动生成 `accounting.db`
- 可直接运行，无需额外数据库配置
- 如果首次运行时报错找不到数据库，可在 `backend` 下手动执行：
  ```bash
  python -c "import models; models.init_db()"
  ```


---

## 🤓 更新new!!!

- 我勒个彩蛋