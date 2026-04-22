# Stage 1: Build the Vue frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Stage 2: Python / Flask API
FROM python:3.11-slim

WORKDIR /app

ENV FLASK_ENV=production

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY config.py run.py seed.py ./
COPY --from=frontend-builder /frontend/dist ./app/static/dist

EXPOSE 5000

CMD ["sh", "-c", "python seed.py && exec gunicorn --bind 0.0.0.0:5000 run:app"]
