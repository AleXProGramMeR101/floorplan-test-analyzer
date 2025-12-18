"""
Модуль конфигурации приложения с поддержкой переменных окружения.
"""

from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any
import os

class Settings(BaseSettings):
    """
    Класс настроек приложения с валидацией типов.
    """
    # Параметры api roboflow
    API_KEY: str = ""
    MODEL_ID: str = "cubicasa5k-2-qpmsa/6"
    
    # Пути к директориям
    INPUT_DIR: str = "./images"
    OUTPUT_DIR: str = "./out"
    DEBUG_DIR: str = "./out/debug"
    
    # Параметры обработки
    CONFIDENCE_THRESHOLD: float = 0.20
    REQUEST_TIMEOUT: int = 60
    
    # Настройки прокси (опционально)
    PROXY_URL: Optional[str] = ''
    
    @property
    def proxies(self) -> Optional[Dict[str, str]]:
        """
        Возвращает словарь с настройками прокси.
        
        Returns:
            Словарь с настройками прокси или None, если прокси не задан
        """
        if self.PROXY_URL:
            return {"http": self.PROXY_URL, "https": self.PROXY_URL}
        return None
    
    @property
    def debug_output_path(self) -> str:
        """
        Возвращает полный путь к директории для отладочных изображений.
        
        Returns:
            Путь к директории отладочной визуализации
        """
        return os.path.join(self.OUTPUT_DIR, "debug")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Экземпляр настроек для использования в приложении
settings = Settings()