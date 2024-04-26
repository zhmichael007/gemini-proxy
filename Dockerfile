FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get clean && apt-get update && \
    apt-get install -y uvicorn
COPY main.py ./
ENV HOST 0.0.0.0
EXPOSE 4000/tcp
CMD ["python3", "main.py"]