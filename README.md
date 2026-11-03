# Архитектура RAG: поиск и сборка контекста на Python

Небольшой воспроизводимый пример XNova показывает границу между поиском и генерацией в RAG. Программа загружает пять учебных документов, проверяет их структуру, выбирает фрагмент по совпадающим словам и собирает контекст с `id` и источником.

Генератор и языковая модель здесь не запускаются. Пример не обращается к сети, API или пользовательским файлам и не требует ключей доступа.

## Что понадобится

- Python 3.12;
- Git;
- терминал.

## Установка

```bash
git clone https://github.com/xnova-tech/rag-architecture-python-example.git
cd rag-architecture-python-example
python3.12 -m venv .venv
```

Активируйте окружение:

- macOS и Linux: `source .venv/bin/activate`;
- Windows PowerShell: `.venv\Scripts\Activate.ps1`;
- Windows cmd: `.venv\Scripts\activate.bat`.

Установите закреплённую тестовую зависимость:

```bash
python -m pip install -r requirements-dev.txt
```

## Запуск примера

```bash
python -I rag_context_demo.py
```

Ожидаемый вывод:

```text
question: Что делать при HTTP 503 у API?
selected: d01 (runbooks/api-503.md)
context:
[d01] runbooks/api-503.md
При HTTP 503 у API проверьте журнал ошибок и доступность upstream.
generator_called: false
```

`HTTP 503` — строка из локального учебного корпуса, а не результат сетевого запроса.

## Запуск тестов

```bash
python -m pytest -q
```

Десять тестов проверяют успешный поиск, пустую выдачу, лексический промах на перефразировании, устойчивый порядок при равной оценке, повторный `id`, неверную форму JSON и записей, `k=0`, Unicode-токены и сохранение источника в контексте.

## Структура

- `rag_context_demo.py` — загрузка, валидация, лексический поиск и сборка контекста;
- `documents.json` — пять искусственных документов;
- `tests/test_rag_context.py` — pytest-контракт примера;
- `pytest.ini` — корень импортов и каталог тестов;
- `.github/workflows/check.yml` — проверки на Linux, macOS и Windows.

Это демонстрация orchestration на маленьком корпусе. Она не оценивает embeddings, vector store, retrieval metrics, вызов LLM или качество сгенерированного ответа.

Исходники распространяются по Apache-2.0; условия находятся в `LICENSE`.
