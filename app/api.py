from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import get_or_create_image, get_comparison, create_comparison
from app.utils import load_image, save_temp_file
from app.compare import ComparisonAlgorithm, AlgorithmParams, AlgorithmParamsBuilder
from app.models import CompareRequest
from app.statistics import get_statistics
from pydantic import ValidationError

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return templates.TemplateResponse("error.html", {"request": request, "message": str(exc)}, status_code=400)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Укажите путь к папке с шаблонами
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):

    """
    Главная страница приложения.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.post(
    "/compare/",
    summary="Compare two images",
    description="Compares two images using the specified algorithm (ORB, Histogram, or Perceptual Hashing).",
    response_class=HTMLResponse,
)
async def compare_images(
    request: Request,
    input1: str = Form(...),  # Получаем URL в виде строки из формы
    input2: str = Form(...),
    method: str = Form("orb"),
    db: Session = Depends(get_db)
):
    """
    Сравнение изображений через форму HTML.
    """
    if method not in ["orb", "hist", "phash"]:
        raise HTTPException(status_code=400, detail="Invalid method")

    try:
        # Валидируем и преобразуем входные данные в объект Pydantic
        compare_request = CompareRequest(input1=input1, input2=input2, method=method)

        # Преобразуем HttpUrl в строку
        input1_url = str(compare_request.input1)
        input2_url = str(compare_request.input2)

        # Получаем или создаем записи изображений
        image1 = get_or_create_image(db, input1_url)
        image2 = get_or_create_image(db, input2_url)

        # Проверяем кэш
        existing = get_comparison(db, image1.hash, image2.hash, method)
        if existing:
            return templates.TemplateResponse(
                "compare.html",
                {
                    "request": request,
                    "input1": input1_url,
                    "input2": input2_url,
                    "method": method,
                    "similarity_score": existing.similarity,
                },
            )

        # Загружаем изображения
        img1 = load_image(input1_url)
        img2 = load_image(input2_url)

        # Сохраняем временные файлы
        img1_path = save_temp_file(img1)
        img2_path = save_temp_file(img2)

        # Сравниваем изображения
        params = (AlgorithmParamsBuilder()
                  .add_img1(img1_path)
                  .add_img2(img2_path)
                  .add_algorithm(method)
                  .build())
        # similarity = ComparisonAlgorithm.compare_images(params)
        params = AlgorithmParams(img1_path=input1, img2_path=input2, algorithm=method)
        similarity = ComparisonAlgorithm.compare_images(params)

        # Сохраняем результат
        create_comparison(db, image1.hash, image2.hash, method, similarity)

        return templates.TemplateResponse(
            "compare.html",
            {
                "request": request,
                "input1": input1_url,
                "input2": input2_url,
                "method": method,
                "similarity_score": similarity,
            },
        )
    except ValidationError as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "errors": e.errors()},
        )
    except Exception as e:
        # Обработка любых других ошибок
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "errors": [{"msg": str(e)}]},
        )


@app.get("/stats/", response_class=HTMLResponse)
async def stats_page(request: Request, db: Session = Depends(get_db)):
    """
    Страница со статистикой.
    """
    stats_df = get_statistics(db)
    stats_html = stats_df.to_html(index=False, classes="table table-striped")

    print(f"Rendered HTML:\n{stats_html}")  # Для отладки

    return templates.TemplateResponse(
        "stats.html", {"request": request, "stats_table": stats_html}
    )

