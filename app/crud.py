from sqlalchemy.orm import Session
from app.database import Image, Comparison
from app.utils import hash_url

# Работа с таблицей images
from sqlalchemy.orm import Session
from app.database import Image
from app.utils import hash_url

def get_or_create_image(db: Session, url: str):
    """
    Получает или создает запись изображения в базе данных.

    Args:
        db (Session): Сессия базы данных.
        url (str): URL изображения.

    Returns:
        Image: Объект записи изображения.
    """
    # Вычисляем хэш URL
    image_hash = hash_url(url)

    # Проверяем, есть ли уже запись с таким хэшем
    image = db.query(Image).filter(Image.hash == image_hash).first()
    if not image:
        # Если записи нет, создаем новую
        image = Image(url=url, hash=image_hash)
        db.add(image)
        db.commit()
        db.refresh(image)

    return image


# Работа с таблицей comparisons
def get_comparison(db: Session, hash1: str, hash2: str, method: str):
    """
    Получает сравнение по хэшам изображений.
    """
    return db.query(Comparison).filter(
        Comparison.image1_hash == hash1,
        Comparison.image2_hash == hash2,
        Comparison.method == method
    ).first()

def create_comparison(db: Session, hash1: str, hash2: str, method: str, similarity: float):
    """
    Создает новую запись сравнения.
    """
    comparison = Comparison(
        image1_hash=hash1, image2_hash=hash2, method=method, similarity=similarity
    )
    db.add(comparison)
    db.commit()
    db.refresh(comparison)
    return comparison
