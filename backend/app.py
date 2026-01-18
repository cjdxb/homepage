from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# 使用绝对路径确保数据库文件位置正确
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'homepage.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app, supports_credentials=True)
db = SQLAlchemy(app)

# 数据库模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Shortcut(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    icon = db.Column(db.String(500), nullable=True)
    order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'icon': self.icon,
            'order': self.order
        }


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wallpaper_mode = db.Column(db.String(20), default='bing')  # bing, custom, disabled
    custom_wallpaper_url = db.Column(db.String(500), nullable=True)
    default_search_engine_id = db.Column(db.Integer, default=1)
    icp_number = db.Column(db.String(100), nullable=True)  # ICP备案号
    site_title = db.Column(db.String(100), nullable=True)  # 网站标题

    def to_dict(self):
        return {
            'wallpaper_mode': self.wallpaper_mode,
            'custom_wallpaper_url': self.custom_wallpaper_url,
            'default_search_engine_id': self.default_search_engine_id,
            'icp_number': self.icp_number,
            'site_title': self.site_title
        }


class SearchEngine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    url_template = db.Column(db.String(500), nullable=False)  # 使用 {query} 作为搜索词占位符
    icon = db.Column(db.String(500), nullable=True)
    is_default = db.Column(db.Boolean, default=False)  # 是否为预置搜索引擎
    order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url_template': self.url_template,
            'icon': self.icon,
            'is_default': self.is_default,
            'order': self.order
        }


# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated_function


# 初始化数据库
def init_db():
    with app.app_context():
        db.create_all()
        # 创建默认管理员账户（如果不存在）
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
        # 创建默认设置（如果不存在）
        if not Settings.query.first():
            settings = Settings(wallpaper_mode='bing', default_search_engine_id=1)
            db.session.add(settings)
        # 创建默认搜索引擎（如果不存在）
        if not SearchEngine.query.first():
            default_engines = [
                SearchEngine(name='Google', url_template='https://www.google.com/search?q={query}', is_default=True, order=1),
                SearchEngine(name='Bing', url_template='https://www.bing.com/search?q={query}', is_default=True, order=2),
                SearchEngine(name='百度', url_template='https://www.baidu.com/s?wd={query}', is_default=True, order=3),
            ]
            for engine in default_engines:
                db.session.add(engine)
        db.session.commit()


# API路由
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session['user_id'] = user.id
        return jsonify({'message': '登录成功', 'username': user.username})
    return jsonify({'error': '用户名或密码错误'}), 401


@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': '已退出登录'})


@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return jsonify({'authenticated': True, 'username': user.username})
    return jsonify({'authenticated': False})


@app.route('/api/shortcuts', methods=['GET'])
def get_shortcuts():
    shortcuts = Shortcut.query.order_by(Shortcut.order).all()
    return jsonify([s.to_dict() for s in shortcuts])


@app.route('/api/shortcuts', methods=['POST'])
@login_required
def add_shortcut():
    data = request.get_json()
    shortcut = Shortcut(
        name=data.get('name'),
        url=data.get('url'),
        icon=data.get('icon'),
        order=data.get('order', 0)
    )
    db.session.add(shortcut)
    db.session.commit()
    return jsonify(shortcut.to_dict()), 201


@app.route('/api/shortcuts/<int:id>', methods=['PUT'])
@login_required
def update_shortcut(id):
    shortcut = Shortcut.query.get_or_404(id)
    data = request.get_json()
    shortcut.name = data.get('name', shortcut.name)
    shortcut.url = data.get('url', shortcut.url)
    shortcut.icon = data.get('icon', shortcut.icon)
    shortcut.order = data.get('order', shortcut.order)
    db.session.commit()
    return jsonify(shortcut.to_dict())


@app.route('/api/shortcuts/<int:id>', methods=['DELETE'])
@login_required
def delete_shortcut(id):
    shortcut = Shortcut.query.get_or_404(id)
    db.session.delete(shortcut)
    db.session.commit()
    return jsonify({'message': '删除成功'})


@app.route('/api/settings', methods=['GET'])
def get_settings():
    settings = Settings.query.first()
    if not settings:
        settings = Settings(wallpaper_mode='bing')
        db.session.add(settings)
        db.session.commit()
    return jsonify(settings.to_dict())


@app.route('/api/settings', methods=['PUT'])
@login_required
def update_settings():
    settings = Settings.query.first()
    if not settings:
        settings = Settings()
        db.session.add(settings)

    data = request.get_json()
    settings.wallpaper_mode = data.get('wallpaper_mode', settings.wallpaper_mode)
    settings.custom_wallpaper_url = data.get('custom_wallpaper_url', settings.custom_wallpaper_url)
    if 'icp_number' in data:
        settings.icp_number = data.get('icp_number') or None
    if 'site_title' in data:
        settings.site_title = data.get('site_title') or None
    db.session.commit()
    return jsonify(settings.to_dict())


@app.route('/api/bing-wallpaper', methods=['GET'])
def get_bing_wallpaper():
    try:
        response = requests.get(
            'https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=zh-CN',
            timeout=10
        )
        data = response.json()
        if data.get('images'):
            image_url = 'https://www.bing.com' + data['images'][0]['url']
            return jsonify({'url': image_url, 'copyright': data['images'][0].get('copyright', '')})
    except Exception as e:
        print(f"获取Bing壁纸失败: {e}")
    return jsonify({'url': '', 'copyright': ''})


@app.route('/api/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    user = User.query.get(session['user_id'])
    if not user.check_password(old_password):
        return jsonify({'error': '原密码错误'}), 400

    user.set_password(new_password)
    db.session.commit()
    return jsonify({'message': '密码修改成功'})


# 搜索引擎API
@app.route('/api/search-engines', methods=['GET'])
def get_search_engines():
    engines = SearchEngine.query.order_by(SearchEngine.order).all()
    return jsonify([e.to_dict() for e in engines])


@app.route('/api/search-engines', methods=['POST'])
@login_required
def add_search_engine():
    data = request.get_json()
    engine = SearchEngine(
        name=data.get('name'),
        url_template=data.get('url_template'),
        icon=data.get('icon'),
        is_default=False,
        order=data.get('order', 0)
    )
    db.session.add(engine)
    db.session.commit()
    return jsonify(engine.to_dict()), 201


@app.route('/api/search-engines/<int:id>', methods=['PUT'])
@login_required
def update_search_engine(id):
    engine = SearchEngine.query.get_or_404(id)
    data = request.get_json()
    engine.name = data.get('name', engine.name)
    engine.url_template = data.get('url_template', engine.url_template)
    engine.icon = data.get('icon', engine.icon)
    engine.order = data.get('order', engine.order)
    db.session.commit()
    return jsonify(engine.to_dict())


@app.route('/api/search-engines/<int:id>', methods=['DELETE'])
@login_required
def delete_search_engine(id):
    engine = SearchEngine.query.get_or_404(id)
    if engine.is_default:
        return jsonify({'error': '不能删除预置搜索引擎'}), 400
    db.session.delete(engine)
    db.session.commit()
    return jsonify({'message': '删除成功'})


# 天气API
@app.route('/api/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city', '').strip()
    if not city:
        return jsonify({'error': '请提供城市名称'}), 400

    try:
        # 使用wttr.in API获取天气信息
        response = requests.get(
            f'https://wttr.in/{city}?format=j1&lang=zh',
            timeout=10,
            headers={'Accept-Language': 'zh-CN'}
        )
        if response.status_code == 200:
            data = response.json()
            current = data.get('current_condition', [{}])[0]
            weather_info = {
                'city': city,
                'temp': current.get('temp_C', '--'),
                'feels_like': current.get('FeelsLikeC', '--'),
                'humidity': current.get('humidity', '--'),
                'weather_desc': current.get('lang_zh', [{}])[0].get('value', current.get('weatherDesc', [{}])[0].get('value', '未知')),
                'weather_code': current.get('weatherCode', ''),
                'wind_speed': current.get('windspeedKmph', '--'),
                'wind_dir': current.get('winddir16Point', ''),
                'uv_index': current.get('uvIndex', '--'),
                'visibility': current.get('visibility', '--'),
                'pressure': current.get('pressure', '--'),
            }
            return jsonify(weather_info)
        else:
            return jsonify({'error': '获取天气失败'}), 500
    except Exception as e:
        print(f"获取天气失败: {e}")
        return jsonify({'error': str(e)}), 500


# IP定位获取城市
@app.route('/api/location', methods=['GET'])
def get_location():
    try:
        # 获取客户端IP
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if client_ip:
            client_ip = client_ip.split(',')[0].strip()

        # 本地开发时使用空IP让API自动检测
        if client_ip in ['127.0.0.1', 'localhost', '::1']:
            api_url = 'http://ip-api.com/json/?lang=zh-CN'
        else:
            api_url = f'http://ip-api.com/json/{client_ip}?lang=zh-CN'

        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return jsonify({
                    'city': data.get('city', ''),
                    'region': data.get('regionName', ''),
                    'country': data.get('country', ''),
                    'lat': data.get('lat'),
                    'lon': data.get('lon')
                })
        return jsonify({'city': '北京', 'region': '北京', 'country': '中国'})
    except Exception as e:
        print(f"获取位置失败: {e}")
        return jsonify({'city': '北京', 'region': '北京', 'country': '中国'})


@app.route('/api/search-suggestions', methods=['GET'])
def get_search_suggestions():
    query = request.args.get('q', '').strip()
    engine = request.args.get('engine', 'google').lower()

    if not query:
        return jsonify([])

    suggestions = []
    try:
        if engine == 'google':
            response = requests.get(
                'https://suggestqueries.google.com/complete/search',
                params={'client': 'firefox', 'q': query},
                timeout=3
            )
            data = response.json()
            suggestions = data[1] if len(data) > 1 else []
        elif engine == 'bing':
            response = requests.get(
                'https://api.bing.com/osjson.aspx',
                params={'query': query},
                timeout=3
            )
            data = response.json()
            suggestions = data[1] if len(data) > 1 else []
        elif engine == '百度' or engine == 'baidu':
            response = requests.get(
                'https://suggestion.baidu.com/su',
                params={'wd': query, 'cb': ''},
                timeout=3
            )
            # 百度返回的是JSONP格式，需要解析
            text = response.text.strip()
            if text.startswith('(') and text.endswith(')'):
                text = text[1:-1]
            import json
            data = json.loads(text)
            suggestions = data.get('s', [])
        else:
            # 对于自定义搜索引擎，尝试使用Google的建议
            response = requests.get(
                'https://suggestqueries.google.com/complete/search',
                params={'client': 'firefox', 'q': query},
                timeout=3
            )
            data = response.json()
            suggestions = data[1] if len(data) > 1 else []
    except Exception as e:
        print(f"获取搜索建议失败: {e}")

    return jsonify(suggestions[:8])


# 确保数据库表在应用启动时创建
init_db()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
