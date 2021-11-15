FROM python:3.8

WORKDIR /webshop
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "webshop.app:app", "--host", "0.0.0.0", "--port", "8080"]