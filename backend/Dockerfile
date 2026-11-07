FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home --uid 10001 museum
COPY --chown=museum:museum app ./app
COPY --chown=museum:museum scripts ./scripts
COPY --chown=museum:museum migrations ./migrations
COPY --chown=museum:museum alembic.ini .
USER museum
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
