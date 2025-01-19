import pandas as pd
from sqlalchemy.orm import Session
from app.database import Comparison

def get_statistics(db: Session):
    """
    Вычисляет статистику для каждого алгоритма на основе данных из таблицы `comparisons`.

    Args:
        db (Session): Сессия базы данных.

    Returns:
        pd.DataFrame: Таблица со статистикой.
    """
    # Получаем все записи из таблицы `comparisons`
    data = db.query(Comparison).all()

    # Преобразуем данные в Pandas DataFrame
    records = [
        {"method": row.method, "similarity_score": row.similarity}
        for row in data
    ]
    df = pd.DataFrame(records)

    if df.empty:
        return pd.DataFrame(columns=["method", "count", "max", "min", "mean"])

    # Группировка по алгоритму
    stats = df.groupby("method")["similarity_score"].agg(
        count="count", max="max", min="min", mean="mean"
    ).reset_index()

    return stats
