# Image Similarity App

**Image Similarity App** — это веб-приложение для сравнения двух изображений с использованием различных алгоритмов. Приложение разработано на FastAPI и предоставляет интерфейс для загрузки изображений, выбора алгоритма и получения результата схожести.

---

## Функциональность

1. **Сравнение изображений:**
   - Сравнивает два изображения и возвращает оценку их схожести.
   - Поддерживаемые алгоритмы:
     - ORB (Oriented FAST and Rotated BRIEF)
     - Гистограммы (Histogram Comparison)
     - Перцептивное хеширование (Perceptual Hashing, pHash).

2. **Автоматическая документация:**
   - Swagger-документация доступна по адресу `/docs`.

3. **Визуальный интерфейс:**
   - Форма для ввода URL изображений и выбора алгоритма.
   - Страница со статистикой (количество сравнений, минимальная, максимальная и средняя оценка схожести для каждого алгоритма).

4. **Сохранение URL и хэшей:**

   - URL изображений автоматически сохраняются в базе данных.
   - Для каждого URL вычисляется хэш изображения, чтобы избежать повторной загрузки и обработки
---

## Установка и запуск

### Шаг 1: Клонирование репозитория
```bash
git clone https://github.com/azat-khatyn/image-similarity
cd image-similarity
```

### Шаг 2: Установка зависимостей

Создайте и активируйте виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

Установите зависимости:
```bash
pip install -r requirements.txt
```

### Шаг 3: Запуск приложения

Запустите сервер разработки:
```bash
uvicorn app.api:app --reload
```

Приложение будет доступно по адресу [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

## Использование

### 1. Главная страница
На главной странице:
- Введите URL двух изображений.
- Выберите алгоритм сравнения.
- Нажмите кнопку "Compare" для получения результата.

### 2. Swagger-документация
Перейдите на [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs), чтобы просмотреть и протестировать API.

### 3. Статистика
На странице статистики `/stats/` отображаются данные о количестве сравнений, максимальных, минимальных и средних значениях оценки схожести для каждого алгоритма.

---

## Структура проекта

```plaintext
image-similarity/
├── app/
│   ├── api.py            # Основной файл приложения
│   ├── compare.py        # Алгоритмы сравнения изображений
│   ├── crud.py           # Операции с базой данных
│   ├── database.py       # Настройки базы данных
│   ├── models.py         # Модели данных
│   ├── statistics.py     # Вычисление статистики
│   ├── templates/        # HTML-шаблоны
│   └── static/           # Статические файлы (CSS, JS, изображения)
├── tests/                # Тесты приложения
├── main.py               # Точка входа для запуска приложения
├── pytest.ini            # Конфигурация Pytest
├── requirements.txt      # Зависимости проекта
└── README.md             # Документация
```

---

## Поддерживаемые алгоритмы сравнения изображений

1. **ORB (Oriented FAST and Rotated BRIEF):**
   Сравнение изображений по ключевым точкам. Подходит для анализа структурных особенностей.

2. **Histogram Comparison:**
   Сравнение гистограмм изображений. Устойчиво к небольшим изменениям в яркости.

3. **Perceptual Hashing (pHash):**
   Вычисляет хеш изображения для анализа визуального сходства. Устойчиво к изменениям масштаба и сжатия.

---

## Пример использования API

### Эндпойнт: `/compare/`
#### Метод: `POST`
**Описание:** Сравнивает два изображения с использованием выбранного алгоритма.

#### Пример запроса:
```bash
curl -X POST \
  -H "Accept: application/json" \
  -F "input1=https://example.com/image1.jpg" \
  -F "input2=https://example.com/image2.jpg" \
  -F "method=phash" \
  http://127.0.0.1:8000/compare/
```

#### Пример ответа:
```json
{
  "similarity_score": 0.85
}

```

---

## Тестирование

В проекте используется `pytest` для тестирования.

### Запуск всех тестов

Чтобы запустить все тесты в проекте, выполните:

```bash
pytest
```


## Лицензия

Данный проект использует шаблон от [HTML5 UP](https://html5up.net/) и находится под лицензией Creative Commons Attribution 3.0. 
