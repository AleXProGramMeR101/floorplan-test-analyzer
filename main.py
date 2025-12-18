"""
Основной модуль для анализа планов квартир.
"""

import os
import json
import logging
import cv2
from config.settings import settings
from utils.file_utils import ensure_directory_exists, get_image_files, format_path_for_display
from utils.image_utils import read_image, ensure_color_image, get_image_dimensions
from detection.roboflow_client import RoboflowClient
from processing.wall_extractor import extract_walls, visualize_walls
from models.schemas import FloorPlanResult

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("floorplan_analyzer.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("main")

def process_single_image(image_path: str, client: RoboflowClient) -> None:
    """
    Обрабатывает одно изображение плана квартиры.
    
    Последовательность операций:
    1. Чтение изображения
    2. Получение предсказаний от модели
    3. Извлечение информации о стенах
    4. Генерация визуализации для отладки
    5. Сохранение результатов в JSON
    
    Args:
        image_path: Путь к файлу изображения
        client: Клиент для работы с api детекции
    """
    logger.info(f"Начало обработки изображения: {format_path_for_display(image_path)}")

    image = read_image(image_path)
    if image is None:
        logger.error(f"Пропуск обработки: не удалось прочитать изображение {image_path}")
        return

    visualization_image = ensure_color_image(image)
    height, width = get_image_dimensions(image)

    try:
        detection_result = client.infer_image(image_path)
    except Exception as e:
        logger.error(f"Пропуск обработки: ошибка при инференсе изображения {image_path}: {str(e)}")
        return

    predictions = detection_result.get('predictions', [])
    walls = extract_walls(predictions, settings.CONFIDENCE_THRESHOLD)

    if visualization_image is not None:
        visualization_image = visualize_walls(visualization_image, walls)

    file_name = os.path.splitext(os.path.basename(image_path))[0]

    result = FloorPlanResult(
        meta={
            "source": os.path.basename(image_path),
            "shape": [height, width],
            "model_id": settings.MODEL_ID
        },
        walls=walls
    )

    output_path = os.path.join(settings.OUTPUT_DIR, f"{file_name}.json")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result.model_dump(), f, ensure_ascii=False, indent=2)
        logger.info(f"Результат сохранен: {format_path_for_display(output_path)}")
    except IOError as e:
        logger.error(f"Ошибка сохранения результата для {format_path_for_display(image_path)}: {str(e)}")

    if visualization_image is not None:
        debug_path = os.path.join(settings.debug_output_path, f"{file_name}_vis.png")
        try:
            cv2.imwrite(debug_path, visualization_image)
            logger.info(f"Отладочная визуализация сохранена: {format_path_for_display(debug_path)}")
        except Exception as e:
            logger.error(f"Ошибка сохранения визуализации для {format_path_for_display(image_path)}: {str(e)}")

def main() -> None:
    """
    Основная функция приложения.
    
    Выполняет:
    1. Создание необходимых директорий
    2. Инициализацию клиента API
    3. Поиск изображений для обработки
    4. Последовательную обработку каждого изображения
    """
    logger.info("Запуск скрипта анализа планов квартир")

    ensure_directory_exists(settings.OUTPUT_DIR)
    ensure_directory_exists(settings.debug_output_path)

    client = RoboflowClient(
        api_key=settings.API_KEY,
        model_id=settings.MODEL_ID,
        timeout=settings.REQUEST_TIMEOUT,
        proxies=settings.proxies
    )

    image_files = get_image_files(settings.INPUT_DIR)
    logger.info(f"Найдено изображений для обработки: {len(image_files)}")
    
    if not image_files:
        logger.warning(f"В директории {settings.INPUT_DIR} не найдено изображений для обработки")
        return

    for image_path in image_files:
        process_single_image(image_path, client)
    
    logger.info("Обработка всех изображений завершена")

if __name__ == "__main__":
    main()