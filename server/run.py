import uvicorn
from app import app
from scheduler import start_scheduler, stop_scheduler
from utils import LOG_LEVEL


if __name__ == "__main__":
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
    log_config["formatters"]["default"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
    start_scheduler()
    try:
        uvicorn.run(app, host="0.0.0.0", port=1030, log_config=log_config, log_level=LOG_LEVEL)
    except KeyboardInterrupt:
        pass
    finally:
        stop_scheduler()