FROM ubuntu:22.04
RUN apt-get update && apt-get install -y python3.10 python3.10-dev
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]