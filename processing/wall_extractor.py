"""
Модуль для извлечения и обработки информации о стенах из результатов детекции.
"""

import cv2
import numpy as np
import logging
from typing import List, Dict, Any, Tuple, Optional
from config.settings import settings

logger = logging.getLogger(__name__)

def bbox_to_wall_line(x: float, y: float, width: float, height: float) -> List[Tuple[int, int]]:
    """
    Преобразует bounding box в линию стены на основе геометрических эвристик.
    
    Args:
        x: X-координата центра bounding box
        y: Y-координата центра bounding box
        width: Ширина bounding box
        height: Высота bounding box
        
    Returns:
        Список точек, определяющих геометрию стены
    """

    x1 = int(x - width / 2)
    y1 = int(y - height / 2)
    x2 = int(x + width / 2)
    y2 = int(y + height / 2)

    if width >= 2 * height:
        # Горизонтальная стена
        y_mid = (y1 + y2) // 2
        return [(x1, y_mid), (x2, y_mid)]
    elif height >= 2 * width:
        # Вертикальная стена
        x_mid = (x1 + x2) // 2
        return [(x_mid, y1), (x_mid, y2)]
    else:
        # Прямоугольная область (маленькие или квадратные объекты)
        return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]

def extract_walls(predictions: List[Dict[str, Any]], 
                 confidence_threshold: float = 0.25) -> List[Dict[str, Any]]:
    """
    Извлекает информацию о стенах из предсказаний модели.
    
    Args:
        predictions: Список предсказаний от модели
        confidence_threshold: Минимальный порог уверенности
        
    Returns:
        Список словарей с информацией о стенах
    """
    walls = []
    wall_id = 1
    
    for pred in predictions:
        try:
            confidence = float(pred.get('confidence', 0.0))
            class_name = str(pred.get('class', '')).lower()
            
            if confidence < confidence_threshold:
                continue

            if 'wall' not in class_name:
                continue

            x = float(pred.get('x', 0))
            y = float(pred.get('y', 0))
            width = float(pred.get('width', 0))
            height = float(pred.get('height', 0))
            
            points = bbox_to_wall_line(x, y, width, height)

            walls.append({
                'id': f"w{wall_id}",
                'points': points,
                'confidence': confidence
            })
            wall_id += 1
            
        except (TypeError, ValueError) as e:
            logger.warning(f"Ошибка обработки предсказания: {str(e)}")
            continue
    
    logger.info(f"Найдено стен: {len(walls)}")
    return walls

def visualize_walls(image: np.ndarray, walls: List[Dict[str, Any]]) -> np.ndarray:
    """
    Визуализирует обнаруженные стены на изображении для отладки.
    
    Args:
        image: Исходное изображение для наложения визуализации
        walls: Список обнаруженных стен
        
    Returns:
        Изображение с нарисованными стенами
    """
    if image is None:
        raise ValueError("Изображение не может быть None")

    vis_image = image.copy()

    for wall in walls:
        points = wall['points']
        for i in range(len(points) - 1):
            start_point = tuple(points[i])
            end_point = tuple(points[i + 1])
            cv2.line(vis_image, start_point, end_point, (0, 0, 255), 3)
    
    return vis_image