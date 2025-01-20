import cv2
import numpy as np
import requests
import tempfile
import hashlib


def load_image(image_path):
    """Загружает изображение из локального пути или URL."""
    if image_path.startswith("http://") or image_path.startswith("https://"):
        # Загрузка изображения из URL
        response = requests.get(image_path)
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch image from URL: {image_path}")
        image = np.array(bytearray(response.content), dtype=np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_GRAYSCALE)
    else:
        # Загрузка локального изображения
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    return image


def save_temp_file(image):
    """
    Сохраняет изображение во временный файл и возвращает путь к нему.

    Аргументы:
        image (np.ndarray): Изображение в формате NumPy-массива.

    Возвращает:
        str: Путь к временному файлу.
    """
    # Создание временного файла
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        temp_path = tmp.name
        # Сохранение изображения во временный файл
        cv2.imwrite(temp_path, image)
    return temp_path


def hash_url(url: str) -> str:
    """
    Хэширует URL с использованием SHA256.

    Аргументы:
        url (str): URL для хэширования.

    Возвращает:
        str: Хэш в виде строки.
    """
    return hashlib.sha256(url.encode('utf-8')).hexdigest()
