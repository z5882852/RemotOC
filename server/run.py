import uvicorn
import argparse
from app import app
from scheduler import start_scheduler, stop_scheduler
from utils import LOG_LEVEL


def parse_args():
    parser = argparse.ArgumentParser(description="启动 RemoteOC 服务端")
    parser.add_argument("--host", "-H", default="0.0.0.0", help="服务器监听的主机地址，默认 0.0.0.0")
    parser.add_argument("--port", "-P", type=int, default=1030, help="服务器监听的端口，默认 1030")
    
    # 解析参数
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # 配置日志格式
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
    log_config["formatters"]["default"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"

    # 启动调度器
    start_scheduler()
    
    try:
        # 使用解析后的 host 和 port 启动 Uvicorn
        uvicorn.run(app, host=args.host, port=args.port, log_config=log_config, log_level=LOG_LEVEL)
    except KeyboardInterrupt:
        pass
    finally:
        # 停止调度器
        stop_scheduler()
