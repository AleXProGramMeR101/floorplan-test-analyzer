"""
Схемы для валидации данных и обеспечения типобезопасности.
Предоставляют строгую структуру для результатов обработки.
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Tuple

class WallPoint(BaseModel):
    """
    Модель для представления точки стены с координатами x, y.
    """
    x: int
    y: int
    
    def to_tuple(self) -> Tuple[int, int]:
        """Возвращает координаты точки в виде кортежа (x, y)"""
        return (self.x, self.y)

class Wall(BaseModel):
    """
    Модель для представления стены с идентификатором и набором точек.
    """
    id: str
    points: List[List[int]]
    confidence: Optional[float] = None

class Metadata(BaseModel):
    """
    Метаданные результата обработки изображения.
    """
    source: str
    shape: List[int]

class FloorPlanResult(BaseModel):
    """
    Полная структура результата обработки плана квартиры.
    """
    meta: Metadata
    walls: List[Wall]