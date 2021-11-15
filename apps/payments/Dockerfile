FROM python:3.8

WORKDIR /payments
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "payments.app:app", "--host", "0.0.0.0", "--port", "8081"]