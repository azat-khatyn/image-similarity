from sqlalchemy import create_engine, Column, Integer, String, Float, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


DATABASE_URL = f"sqlite:///{os.path.abspath('./similarity.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    hash = Column(String, unique=True, index=True)


class Comparison(Base):
    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True, index=True)
    image1_hash = Column(String, index=True)
    image2_hash = Column(String, index=True)
    method = Column(String, index=True)
    similarity = Column(Float)
    __table_args__ = (
        UniqueConstraint("image1_hash", "image2_hash", "method", name="uq_comparison"),
    )

# Создание таблицы
Base.metadata.create_all(bind=engine)
