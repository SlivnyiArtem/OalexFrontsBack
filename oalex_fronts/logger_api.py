import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, TextIO
import dotenv

dotenv.load_dotenv()


class DualLogger:
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file
        self.file_handle: Optional[TextIO] = None
        self._setup_logger()

    def _setup_logger(self):
        if self.log_file:
            try:
                log_path = Path(self.log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)

                self.file_handle = open(self.log_file, 'a', encoding='utf-8')
                self._write_to_file(f"\n{'=' * 60}")
                self._write_to_file(f"Логирование начато: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                self._write_to_file(f"{'=' * 60}\n")
            except Exception as e:
                self.file_handle = None

    def _write_to_file(self, message: str):
        if self.file_handle:
            try:
                self.file_handle.write(message + '\n')
                self.file_handle.flush()
            except Exception as e:
                print(f"Ошибка записи в лог-файл: {e}", file=sys.stderr)

    def __call__(self, *args, **kwargs):
        sep = kwargs.get('sep', ' ')
        end = kwargs.get('end', '\n')
        file = kwargs.get('file', sys.stdout)

        message = sep.join(str(arg) for arg in args) + end

        file.write(message)

        if self.file_handle and file == sys.stdout:
            file_message = message.rstrip('\n')
            self._write_to_file(file_message)

    def info(self, *args, **kwargs):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"[{timestamp} INFO] " + ' '.join(str(arg) for arg in args)
        print(message, **kwargs)
        if self.file_handle:
            self._write_to_file(message)

    def warning(self, *args, **kwargs):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"[{timestamp} WARNING] " + ' '.join(str(arg) for arg in args)
        print(message, **kwargs)
        if self.file_handle:
            self._write_to_file(message)

    def error(self, *args, **kwargs):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"[{timestamp} ERROR] " + ' '.join(str(arg) for arg in args)
        print(message, **kwargs)
        if self.file_handle:
            self._write_to_file(message)

    def debug(self, *args, **kwargs):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"[{timestamp} DEBUG] " + ' '.join(str(arg) for arg in args)
        print(message, **kwargs)
        if self.file_handle:
            self._write_to_file(message)

    def close(self):
        if self.file_handle:
            self._write_to_file(f"\n{'=' * 60}")
            self._write_to_file(f"Логирование завершено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self._write_to_file(f"{'=' * 60}\n")
            self.file_handle.close()

    def __del__(self):
        self.close()


_log_file_path = os.getenv('LOG_FILE_PATH', 'logs/application.log')
log = DualLogger(_log_file_path)
