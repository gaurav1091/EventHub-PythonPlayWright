FROM mcr.microsoft.com/playwright/python:v1.61.0-noble

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HEADLESS=true \
    BROWSER=chromium

COPY pyproject.toml ./
COPY README.md ./
COPY src ./src
COPY tests ./tests
COPY conftest.py ./

RUN python -m pip install --upgrade pip \
    && python -m pip install -e ".[dev]"

RUN mkdir -p reports test-results

CMD ["pytest"]
