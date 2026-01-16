# Use a slim official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8501

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	gcc \
	&& rm -rf /var/lib/apt/lists/*


COPY requirements.txt ./

RUN python -m pip install --upgrade pip setuptools wheel \
	&& pip install --no-cache-dir -r requirements.txt


COPY . /app


EXPOSE 8501


CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "localhost", "--server.enableCORS", "true"]
