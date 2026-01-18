# Homepage

<div align="center">

[![License](https://img.shields.io/github/license/daidr/homepage?style=flat-square)](./LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/daidr/homepage?style=flat-square)](https://github.com/daidr/homepage/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/daidr/homepage?style=flat-square)](https://github.com/daidr/homepage/network/members)

一个简洁美观的个人导航主页，支持自定义快捷方式、多搜索引擎、天气显示和动态壁纸。

![](./preview.png)

</div>

## ✨ 特性

- **时间与日期显示** - 实时显示当前时间和日期
- **天气信息** - 支持手动设置城市或自动 IP 定位，显示当前天气状况
- **多搜索引擎** - 内置 Google、Bing、百度，支持自定义添加搜索引擎
- **搜索建议** - 输入时实时显示搜索建议
- **快捷方式** - 可自定义添加常用网站快捷方式，自动获取网站图标
- **动态壁纸** - 支持 Bing 每日壁纸、自定义壁纸或纯色背景
- **后台管理** - 完整的后台管理界面，管理快捷方式、搜索引擎和系统设置
- **响应式设计** - 适配桌面端和移动端

## 🖼️ 功能

### 主页
- 大字体时间显示
- 日期和天气信息
- 搜索框（支持切换搜索引擎）
- 快捷方式网格
- Bing 每日壁纸背景

### 后台管理
- 快捷方式管理（增删改查）
- 搜索引擎管理
- 壁纸设置
- 网站设置（标题、ICP备案号）
- 密码修改

## 🛠️ 技术栈

### 前端
- [Vue 3](https://vuejs.org/) + Composition API
- [Vite 5](https://vitejs.dev/) - 构建工具
- [Vue Router 4](https://router.vuejs.org/) - 路由管理
- [Pinia](https://pinia.vuejs.org/) - 状态管理
- [Axios](https://axios-http.com/) - HTTP 客户端

### 后端
- [Python 3.9+](https://www.python.org/)
- [Flask 3.0](https://flask.palletsprojects.com/) - Web 框架
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) - ORM
- [Flask-CORS](https://flask-cors.readthedocs.io/) - 跨域处理
- [SQLite](https://www.sqlite.org/) - 数据库

## 🚀 快速开始

### 环境要求

- [Node.js](https://nodejs.org/) 18+
- [Python](https://www.python.org/) 3.9+

### 本地开发

#### 1. 克隆项目

```bash
git clone https://github.com/yourusername/homepage.git
cd homepage
```

#### 2. 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python app.py
```

后端服务将在 `http://localhost:5000` 运行。

#### 3. 前端启动

```bash
# 在新终端窗口中，进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 `http://localhost:5173` 运行。

#### 4. 访问应用

打开浏览器访问 `http://localhost:5173` 即可访问主页。

### 默认账户

首次启动时会自动创建管理员账户：

- 用户名：`admin`
- 密码：`admin123`

> ⚠️ **安全提醒**：请在首次登录后立即修改密码！

## 📁 项目结构

```
homepage/
├── backend/                    # 后端代码
│   ├── app.py                  # Flask 应用主文件
│   ├── gunicorn.conf.py        # Gunicorn 生产环境配置
│   ├── requirements.txt        # Python 依赖
│   ├── .env.example            # 环境变量示例
│   └── homepage.db             # SQLite 数据库
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── views/
│   │   │   ├── Home.vue        # 主页
│   │   │   ├── Admin.vue       # 后台管理
│   │   │   └── Login.vue       # 登录页
│   │   ├── stores/
│   │   │   └── auth.js         # 认证状态管理
│   │   ├── router/
│   │   │   └── index.js        # 路由配置
│   │   ├── App.vue             # 根组件
│   │   ├── main.js             # 入口文件
│   │   └── config.js           # 配置文件
│   ├── .env.production         # 生产环境配置
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── DEPLOY.md                   # 生产环境部署文档
└── README.md
```

## 🔌 API 接口

### 认证相关
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/login` | 用户登录 |
| POST | `/api/logout` | 用户登出 |
| GET | `/api/check-auth` | 检查登录状态 |
| POST | `/api/change-password` | 修改密码 |

### 快捷方式管理
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/shortcuts` | 获取所有快捷方式 |
| POST | `/api/shortcuts` | 添加快捷方式（需登录）|
| PUT | `/api/shortcuts/:id` | 更新快捷方式（需登录）|
| DELETE | `/api/shortcuts/:id` | 删除快捷方式（需登录）|

### 搜索引擎管理
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/search-engines` | 获取所有搜索引擎 |
| POST | `/api/search-engines` | 添加搜索引擎（需登录）|
| PUT | `/api/search-engines/:id` | 更新搜索引擎（需登录）|
| DELETE | `/api/search-engines/:id` | 删除搜索引擎（需登录）|

### 系统设置
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/settings` | 获取系统设置 |
| PUT | `/api/settings` | 更新系统设置（需登录）|

### 其他接口
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/bing-wallpaper` | 获取 Bing 每日壁纸 |
| GET | `/api/weather` | 获取天气信息 |
| GET | `/api/location` | IP 定位获取城市 |
| GET | `/api/search-suggestions` | 获取搜索建议 |

## ⚙️ 配置说明

### 后端环境变量

创建 `backend/.env` 文件：

```bash
# Flask 密钥（生产环境必须修改）
SECRET_KEY=your-super-secret-key-change-this

# Flask 环境
FLASK_ENV=development
```

### 前端环境变量

创建 `frontend/.env` 文件：

```bash
# API 地址配置
VITE_API_BASE_URL=http://localhost:5000
```

## 📦 生产环境部署

详细的生产环境部署步骤请参考 [DEPLOY.md](./DEPLOY.md)。

## 📄 许可证

本项目采用 [MIT License](./LICENSE)。
