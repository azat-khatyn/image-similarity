import pandas as pd
from sqlalchemy.orm import Session
from app.database import Comparison
import plotly.express as px

def get_statistics(db: Session):
    """
    Вычисляет статистику для каждого алгоритма на основе данных из таблицы `comparisons`.

     Аргументы:
        db (Session): Сессия базы данных.

    Возвращает:
        pd.DataFrame: Таблица со статистикой.
    """
    # Получение всех записей из таблицы `comparisons`
    data = db.query(Comparison).all()

    # Преобразование данных в pandas DataFrame
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

    fig = px.bar(stats, x="method", y="count", title="Comparison Counts by Method")
    fig.update_layout(xaxis_title="Method", yaxis_title="Count", template="plotly_white")

    # Экспорт графика в HTML
    plot_html = fig.to_html(full_html=False)

    return {
        "stats_table": stats,
        "plot_html": plot_html,
    }
