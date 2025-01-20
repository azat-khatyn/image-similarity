from abc import ABC, abstractmethod
import cv2
from app.utils import load_image
from pydantic import BaseModel
from PIL import Image
import imagehash
import logging
from pydantic import BaseModel


#  Применение паттерна Builder
class AlgorithmParams(BaseModel):
    img1_path: str
    img2_path: str
    algorithm: str

class AlgorithmParamsBuilder:
    def __init__(self):
        self.params = {}

    def add_img1(self, img1_path: str):
        self.params["img1_path"] = img1_path
        return self

    def add_img2(self, img2_path: str):
        self.params["img2_path"] = img2_path
        return self

    def add_algorithm(self, algorithm: str):
        self.params["algorithm"] = algorithm
        return self

    def build(self):
        return AlgorithmParams(**self.params)


# Применение паттерна Strategy
class ComparisonStrategy(ABC):
    @abstractmethod
    def compare(self, img1_path: str, img2_path: str) -> float:
        """
        Сравнивает два изображения и возвращает значение сходства.
        """
        pass

# Стратегия ORB
class ORBStrategy(ComparisonStrategy):
    def compare(self, img1_path: str, img2_path: str) -> float:
        img1 = load_image(img1_path)
        img2 = load_image(img2_path)

        if img1 is None or img2 is None:
            raise ValueError("One or both images could not be loaded.")

        orb = cv2.ORB_create()
        kp1, des1 = orb.detectAndCompute(img1, None)
        kp2, des2 = orb.detectAndCompute(img2, None)

        if des1 is None or des2 is None:
            return 0

        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        matches = sorted(matches, key=lambda x: x.distance)

        return len(matches) / max(len(kp1), len(kp2))

# Стратегия гистограмм
class HistogramStrategy(ComparisonStrategy):
    def compare(self, img1_path: str, img2_path: str) -> float:
        img1 = load_image(img1_path)
        img2 = load_image(img2_path)

        if img1 is None or img2 is None:
            raise ValueError("One or both images could not be loaded.")

        hist1 = cv2.calcHist([img1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([img2], [0], None, [256], [0, 256])

        cv2.normalize(hist1, hist1)
        cv2.normalize(hist2, hist2)

        return cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

# Стратегия pHash
class PHashStrategy(ComparisonStrategy):
    def compare(self, img1_path: str, img2_path: str) -> float:
        try:
            # Используем load_image для загрузки изображений
            img1 = load_image(img1_path)
            img2 = load_image(img2_path)

            # Преобразуем OpenCV изображение в формат, совместимый с Pillow
            img1 = Image.fromarray(cv2.cvtColor(img1, cv2.COLOR_BGR2RGB))
            img2 = Image.fromarray(cv2.cvtColor(img2, cv2.COLOR_BGR2RGB))

            # Вычисляем pHash
            hash1 = imagehash.phash(img1)
            hash2 = imagehash.phash(img2)

            max_distance = len(hash1.hash) ** 2
            distance = (hash1 - hash2)
            return 1 - (distance / max_distance)
        except Exception as e:
            logging.error(f"Error in pHash comparison: {e}")
            raise ValueError(f"Error comparing images with pHash: {e}")

# Основной класс для выбора стратегии
class ComparisonAlgorithm:
    _strategies = {
        "orb": ORBStrategy(),
        "hist": HistogramStrategy(),
        "phash": PHashStrategy(),
    }

    @classmethod
    def compare_images(cls, params):
        strategy = cls._strategies.get(params.algorithm)
        if not strategy:
            raise ValueError(f"Unknown algorithm `{params.algorithm}`!")
        return strategy.compare(params.img1_path, params.img2_path)
