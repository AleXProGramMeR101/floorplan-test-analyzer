"""
Утилиты для работы с файловой системой: создание директорий, поиск файлов и т.д.
"""

import os
import logging
from typing import List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

def ensure_directory_exists(path: str) -> None:
    """
    Проверяет существование директории по указанному пути.

    Args:
        path: Путь к директории, которую необходимо создать
    """
    if not path or not isinstance(path, str):
        raise ValueError("Некорректный путь к директории")
    
    try:
        os.makedirs(path, exist_ok=True)
        logger.debug(f"Директория создана или уже существует: {path}")
    except OSError as e:
        logger.error(f"Ошибка при создании директории {path}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при создании директории {path}: {str(e)}")
        raise

def get_image_files(directory: str, extensions: Optional[Tuple[str, ...]] = None) -> List[str]:
    """
    Получает список файлов изображений в указанной директории.

    Args:
        directory: Путь к директории с изображениями
        extensions: Кортеж допустимых расширений файлов. По умолчанию: ('.jpg', '.jpeg', '.png')
        
    Returns:
        Список абсолютных путей к файлам изображений
    """
    if extensions is None:
        extensions = ('.jpg', '.jpeg', '.png')

    if not os.path.exists(directory):
        logger.warning(f"Директория не существует: {directory}")
        return []
    
    if not os.path.isdir(directory):
        logger.error(f"Указанный путь не является директорией: {directory}")
        raise ValueError(f"Путь {directory} не является директорией")

    image_files = []
    for filename in os.listdir(directory):
        if any(filename.lower().endswith(ext) for ext in extensions):
            full_path = os.path.join(directory, filename)
            image_files.append(full_path)
    
    logger.info(f"Найдено {len(image_files)} изображений в директории {directory}")
    return image_files

def format_path_for_display(path: str) -> str:
    """
    Нормализует путь к файлу для вывода.
    
    Args:
        path: Исходный путь
        
    Returns:
        Правильный путь
    """
    if not path:
        return ""
    return str(Path(path)).replace("\\", "/")