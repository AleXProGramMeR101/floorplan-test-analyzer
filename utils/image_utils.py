"""
Набор утилит для работы с изображениями с обработкой ошибок и валидацией типов.
"""

import cv2
import numpy as np
import logging
from typing import Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

def read_image(image_path: str) -> Optional[np.ndarray]:
    """
    Надежное чтение изображения с обработкой возможных ошибок.
    
    Args:
        image_path: Путь к файлу изображения
        
    Returns:
        Массив numpy с изображением или None в случае ошибки
    """
    try:
        img = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)
        if img is not None:
            return img

        with open(image_path, 'rb') as f:
            img_bytes = bytearray(f.read())
        img_arr = np.asarray(img_bytes, dtype=np.uint8)
        img = cv2.imdecode(img_arr, cv2.IMREAD_UNCHANGED)
        
        if img is None:
            logger.error(f"Не удалось декодировать изображение: {image_path}")
            return None
            
        return img
    except Exception as e:
        logger.error(f"Критическая ошибка при чтении изображения {image_path}: {str(e)}")
        return None

def ensure_color_image(image: np.ndarray) -> np.ndarray:
    """
    Преобразует изображение в 3-канальный цветной формат BGR для визуализации.
    
    Args:
        image: Входное изображение
        
    Returns:
        3-канальное BGR изображение
    """
    if image is None:
        raise ValueError("Изображение не может быть None")
    
    # Обработка одноканальных изображений (серых)
    if len(image.shape) == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    
    # Обработка изображений с альфа-каналом (4 канала)
    if image.shape[2] == 4:
        return cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    
    # Копирование для избежания изменений исходного изображения
    return image.copy()

def get_image_dimensions(image: np.ndarray) -> Tuple[int, int]:
    """
    Возвращает размеры изображения в формате (высота, ширина).
    
    Args:
        image: Входное изображение
        
    Returns:
        Кортеж (высота, ширина)
    """
    if image is None:
        raise ValueError("Изображение не может быть None")
    return image.shape[:2]