import cv2
from app.utils import load_image
from pydantic import BaseModel


# next two classes - pattern builder
from pydantic import BaseModel

class AlgorithmParams(BaseModel):
    img1_path: str
    img2_path: str
    algorithm: str

class AlgorithmParamsBuilder:
    def __init__(self):
        self.img1_path = None
        self.img2_path = None
        self.algorithm = None

    def add_img1(self, img1_path: str):
        self.img1_path = img1_path
        return self

    def add_img2(self, img2_path: str):
        self.img2_path = img2_path
        return self

    def add_algorithm(self, algorithm: str):
        self.algorithm = algorithm
        return self

    def build(self):
        # Передаем параметры как именованные аргументы
        return AlgorithmParams(
            img1_path=self.img1_path,
            img2_path=self.img2_path,
            algorithm=self.algorithm
        )


# singleton pattern
class ComparisonAlgorithm:
    @classmethod
    def compare_images(cls, params: AlgorithmParams) -> float:
        if params.algorithm == "orb":
            similarity = cls._compare_images_with_orb(params.img1_path, params.img2_path)
        elif params.algorithm == "hist":
            similarity = cls._compare_images_hist(params.img1_path, params.img2_path)
        else:
            raise Exception(f"Unknown algorithm `{params.algorithm}`!")
        return similarity

    @staticmethod
    def _compare_images_hist(img1_path: str, img2_path: str) -> float:
        """Сравнивает два изображения на основе гистограмм."""
        # Загрузка изображений
        img1 = load_image(img1_path)
        img2 = load_image(img2_path)

        # Проверка наличия изображений
        if img1 is None or img2 is None:
            raise ValueError("One or both images could not be loaded.")

        # Вычисление гистограмм и сравнение
        hist1 = cv2.calcHist([img1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([img2], [0], None, [256], [0, 256])

        cv2.normalize(hist1, hist1)
        cv2.normalize(hist2, hist2)

        similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        return similarity

    @staticmethod
    def _compare_images_with_orb(img1_path, img2_path):
        """Сравнение изображений с помощью ORB (ключевых точек)."""
        # Используем load_image для загрузки изображений из локальных путей или URL
        img1 = load_image(img1_path)
        img2 = load_image(img2_path)

        # Проверка наличия изображений
        if img1 is None or img2 is None:
            raise ValueError("One or both images could not be loaded.")

        # Инициализация ORB
        orb = cv2.ORB_create()

        # Поиск ключевых точек и вычисление дескрипторов
        kp1, des1 = orb.detectAndCompute(img1, None)
        kp2, des2 = orb.detectAndCompute(img2, None)

        # Проверка наличия дескрипторов
        if des1 is None or des2 is None:
            return 0  # Если ключевых точек недостаточно

        # Матчер дескрипторов (Brute-Force)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)

        # Сортировка матчей по расстоянию
        matches = sorted(matches, key=lambda x: x.distance)

        # Вычисление оценки схожести
        score = len(matches) / max(len(kp1), len(kp2))
        return score
