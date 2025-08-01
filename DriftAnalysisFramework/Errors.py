import threading


class ErrorManager:
    error_array = []
    _lock = threading.Lock()

    @classmethod
    def add_error(cls, error_message):
        with cls._lock:
            cls.error_array.append(error_message)


error_instance = ErrorManager()

