"""
Клиент для взаимодействия с api roboflow для детекции объектов на изображениях.
"""

import requests
import logging
from typing import Dict, Any, Optional
from requests.exceptions import RequestException
from config.settings import settings

logger = logging.getLogger(__name__)

class RoboflowClient:
    """
    Инкапсулирует логику запросов, обработки ошибок и параметризацию взаимодействия с api.
    """
    
    def __init__(self, api_key: str, model_id: str, timeout: int = 60, proxies: Optional[Dict[str, str]] = None):
        """
        Инициализация клиента roboflow.
        
        Args:
            api_key: Ключ API для аутентификации
            model_id: Идентификатор модели
            timeout: Таймаут запроса в секундах
            proxies: Настройки прокси для requests
        """
        self.api_key = api_key
        self.model_id = model_id
        self.timeout = timeout
        self.proxies = proxies
        self.base_url = f"https://detect.roboflow.com/{model_id}"
    
    def infer_image(self, image_path: str) -> Dict[str, Any]:
        """
        Отправляет изображение в api roboflow для инференса.
        
        Args:
            image_path: Путь к файлу изображения
            
        Returns:
            Словарь с результатами детекции
        """
        url = f"{self.base_url}?api_key={self.api_key}"
        
        try:
            logger.debug(f"Отправка изображения в api roboflow: {image_path}")
            with open(image_path, 'rb') as image_file:
                files = {'file': image_file}
                response = requests.post(
                    url,
                    files=files,
                    proxies=self.proxies,
                    timeout=self.timeout,
                    verify=True
                )

            logger.debug(f"Статус ответа: {response.status_code}")
            if response.status_code != 200:
                logger.warning(f"Некорректный статус ответа: {response.status_code}")
                logger.debug(f"Тело ответа: {response.text[:500]}...")
            
            response.raise_for_status()
            result = response.json()

            if "predictions" not in result:
                logger.error("Ответ API не содержит поля 'predictions'")
                raise ValueError("Некорректная структура ответа от API")
                
            return result
            
        except RequestException as e:
            logger.error(f"Ошибка сети при запросе к api roboflow: {str(e)}")
            if e.response is not None:
                logger.error(f"Детали ответа: {e.response.text[:500]}...")
            raise
        except IOError as e:
            logger.error(f"Ошибка чтения файла изображения {image_path}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Неожиданная ошибка при инференсе: {str(e)}")
            raise