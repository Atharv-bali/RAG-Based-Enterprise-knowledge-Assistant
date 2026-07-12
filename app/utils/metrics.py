import threading
import time

class MetricsCollector:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(MetricsCollector, cls).__new__(cls, *args, **kwargs)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._lock = threading.Lock()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_latency = 0.0
        self.min_latency = float('inf')
        self.max_latency = 0.0
        self.start_time = time.time()
        self._initialized = True

    def record_request(self, success: bool, latency: float):
        with self._lock:
            self.total_requests += 1
            if success:
                self.successful_requests += 1
            else:
                self.failed_requests += 1
            self.total_latency += latency
            if latency < self.min_latency:
                self.min_latency = latency
            if latency > self.max_latency:
                self.max_latency = latency

    def get_metrics(self) -> dict:
        with self._lock:
            uptime = time.time() - self.start_time
            avg_latency = (self.total_latency / self.total_requests) if self.total_requests > 0 else 0.0
            return {
                "uptime_seconds": round(uptime, 2),
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "average_latency_seconds": round(avg_latency, 4),
                "min_latency_seconds": round(self.min_latency, 4) if self.min_latency != float('inf') else 0.0,
                "max_latency_seconds": round(self.max_latency, 4),
            }

# Singleton instance
metrics_collector = MetricsCollector()
