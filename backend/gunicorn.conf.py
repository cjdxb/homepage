# Gunicorn 生产环境配置文件

import multiprocessing
import os

# 绑定地址和端口
bind = os.environ.get('GUNICORN_BIND', '0.0.0.0:9320')

# Worker 配置
# 推荐的 worker 数量: (2 * CPU核心数) + 1
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
threads = 2

# 超时设置
timeout = 30
keepalive = 2
graceful_timeout = 30

# 请求限制
max_requests = 1000
max_requests_jitter = 50

# 日志配置
accesslog = os.environ.get('GUNICORN_ACCESS_LOG', '-')  # '-' 表示输出到 stdout
errorlog = os.environ.get('GUNICORN_ERROR_LOG', '-')    # '-' 表示输出到 stderr
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程配置
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# 服务器钩子
def on_starting(server):
    """服务器启动前调用"""
    pass

def on_reload(server):
    """服务器重载时调用"""
    pass

def worker_int(worker):
    """Worker 收到 INT 或 QUIT 信号时调用"""
    pass

def worker_abort(worker):
    """Worker 收到 SIGABRT 信号时调用"""
    pass

# 预加载应用 (提高性能，但会增加内存使用)
preload_app = True

# 进程名称
proc_name = 'homepage-backend'

# 安全设置
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
