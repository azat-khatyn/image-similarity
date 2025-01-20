from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import get_or_create_image, get_comparison, create_comparison
from app.utils import load_image, save_temp_file
from app.compare import ComparisonAlgorithm, AlgorithmParamsBuilder
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

# Путь к папке с шаблонами
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
    method: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Сравнение изображений через API или HTML-форму.
    """
    if method not in ["orb", "hist", "phash"]:
        raise HTTPException(status_code=400, detail="Invalid method")

    try:
        # Валидация и преобразование входных данные в объект Pydantic
        compare_request = CompareRequest(input1=input1, input2=input2, method=method)

        # Преобразование HttpUrl в строку
        input1_url = str(compare_request.input1)
        input2_url = str(compare_request.input2)

        # Получение или создание записи изображений
        image1 = get_or_create_image(db, input1_url)
        image2 = get_or_create_image(db, input2_url)

        # Проверка кэша
        existing = get_comparison(db, image1.hash, image2.hash, method)
        if existing:
            similarity = existing.similarity
        else:
            # Загрузка изображения
            img1 = load_image(input1_url)
            img2 = load_image(input2_url)

            # Сохранение временных файлов
            img1_path = save_temp_file(img1)
            img2_path = save_temp_file(img2)

            # Сравнение изображений
            params = (AlgorithmParamsBuilder()
                      .add_img1(img1_path)
                      .add_img2(img2_path)
                      .add_algorithm(method)
                      .build())
            similarity = ComparisonAlgorithm.compare_images(params)

            # Сохранение результата в базу данных
            create_comparison(db, image1.hash, image2.hash, method, similarity)

        # Если запрос через API (Accept: application/json)
        if request.headers.get("accept", "").lower() == "application/json":
            return JSONResponse(content={"similarity_score": similarity})

        # По умолчанию возвращаем HTML
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
        return JSONResponse(content={"error": e.errors()}, status_code=422)
    except Exception as e:
        # Обработка любых других ошибок
        return JSONResponse(content={"error": str(e)}, status_code=500)


# async def compare_images(
#     request: Request,
#     input1: str = Form(...),  # Получаем URL в виде строки из формы
#     input2: str = Form(...),
#     method: str = Form("orb"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Сравнение изображений через форму HTML.
#     """
#     if method not in ["orb", "hist", "phash"]:
#         raise HTTPException(status_code=400, detail="Invalid method")
#
#     try:
#         # Валидация и преобразование входных данные в объект Pydantic
#         compare_request = CompareRequest(input1=input1, input2=input2, method=method)
#
#         # Преобразование HttpUrl в строку
#         input1_url = str(compare_request.input1)
#         input2_url = str(compare_request.input2)
#
#         # Получение или создание записи изображений
#         image1 = get_or_create_image(db, input1_url)
#         image2 = get_or_create_image(db, input2_url)
#
#         # Проверка кэша
#         existing = get_comparison(db, image1.hash, image2.hash, method)
#         if existing:
#             return templates.TemplateResponse(
#                 "compare.html",
#                 {
#                     "request": request,
#                     "input1": input1_url,
#                     "input2": input2_url,
#                     "method": method,
#                     "similarity_score": existing.similarity,
#                 },
#             )
#
#         # Загрузка изображения
#         img1 = load_image(input1_url)
#         img2 = load_image(input2_url)
#
#         # Сохранение временных файлов
#         img1_path = save_temp_file(img1)
#         img2_path = save_temp_file(img2)
#
#         # Сравнение изображений
#         params = (AlgorithmParamsBuilder()
#                   .add_img1(img1_path)
#                   .add_img2(img2_path)
#                   .add_algorithm(method)
#                   .build())
#         similarity = ComparisonAlgorithm.compare_images(params)
#
#         # Сохранение результата в базу данных
#         create_comparison(db, image1.hash, image2.hash, method, similarity)
#
#         # Проверка заголовка Accept
#         accept_header = request.headers.get("accept", "").lower()
#         print(f"Accept header: {accept_header}")  # Для отладки
#
#         if "application/json" in accept_header:
#             return JSONResponse(content={"similarity_score": similarity})
#         else:
#             return HTMLResponse(content=f"<html><body><h1>Similarity: {similarity}</h1></body></html>")
#
#     except Exception as e:
#         return JSONResponse(content={"error": "Comparison failed", "details": str(e)}, status_code=500)


@app.post("/test/")
async def test_endpoint(request: Request):
    accept_header = request.headers.get("accept", "").lower()
    print(f"Accept header received: {accept_header}")
    if "application/json" in accept_header:
        return JSONResponse(content={"message": "JSON response"})
    return HTMLResponse(content="<html><body><h1>HTML response</h1></body></html>")

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
