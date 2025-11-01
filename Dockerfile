FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn
COPY . .
EXPOSE 8000
CMD ["gunicorn", "app.main:app", "-b", "0.0.0.0:8000", "-w", "4", "-k", "uvicorn.workers.UvicornWorker"]