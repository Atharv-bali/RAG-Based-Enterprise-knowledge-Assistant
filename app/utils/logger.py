import os
import time
import logging
from logging.handlers import RotatingFileHandler
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.metrics import metrics_collector

# Ensure logs directory exists
LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

# Logger setup
logger = logging.getLogger("rag_api")
logger.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s (Line %(lineno)d): %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# API log handler (INFO and above)
api_log_path = os.path.join(LOGS_DIR, "api.log")
api_handler = RotatingFileHandler(api_log_path, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")
api_handler.setLevel(logging.INFO)
api_handler.setFormatter(formatter)
logger.addHandler(api_handler)

# Error log handler (ERROR and above)
error_log_path = os.path.join(LOGS_DIR, "error.log")
error_handler = RotatingFileHandler(error_log_path, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)
logger.addHandler(error_handler)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_host = request.client.host if request.client else "unknown"
        logger.info(f"Incoming Request: {request.method} {request.url.path} from {client_host}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log endpoints other than metrics/health at debug or info, let's keep all info
            status_code = response.status_code
            logger.info(
                f"Completed Request: {request.method} {request.url.path} - "
                f"Status: {status_code} - Latency: {process_time:.4f}s"
            )
            
            # Record metrics for API endpoints (excluding /health, /metrics, /)
            if request.url.path not in ["/health", "/metrics", "/"]:
                success = 200 <= status_code < 400
                metrics_collector.record_request(success, process_time)
                
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Failed Request: {request.method} {request.url.path} - "
                f"Error: {str(e)} - Latency: {process_time:.4f}s",
                exc_info=True
            )
            if request.url.path not in ["/health", "/metrics", "/"]:
                metrics_collector.record_request(False, process_time)
            raise e
