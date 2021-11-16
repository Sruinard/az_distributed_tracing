from pydantic import BaseModel
import json

import requests
import uvicorn
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from webshop.config import Config
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
import redis


class Order(BaseModel):
    item_id: int
    quantity: int
    price: float


templates = Jinja2Templates(directory="templates/")
load_dotenv()
REDIS = redis.StrictRedis(host=Config.REDIS_HOST,
                          port=Config.REDIS_PORT, db=0,  password=Config.REDIS_PASS, ssl=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

trace.set_tracer_provider(TracerProvider(
    resource=Resource.create({SERVICE_NAME: "webshop"})
))
tracer = trace.get_tracer(__name__)


@app.on_event("startup")
def startup_event():
    # This line causes your calls made with the requests library to be tracked.
    span_processor = BatchSpanProcessor(
        AzureMonitorTraceExporter.from_connection_string(
            Config.APPINSIGHTS_CONNECTION_STRING
        )
    )
    trace.get_tracer_provider().add_span_processor(span_processor)

    RedisInstrumentor().instrument()
    RequestsInstrumentor().instrument()
    FastAPIInstrumentor.instrument_app(
        app, tracer_provider=trace.get_tracer_provider())


@app.get("/")
async def get():
    result = REDIS.ping()
    return "Ping returned by redis is: " + str(result)


@app.get("/orders/{item_id}")
async def get_order(item_id: int):
    cached_response = REDIS.get(item_id)
    if cached_response:
        response = json.loads(cached_response)
    else:
        response = requests.get(
            f"{Config.SHIPMENTS_ENDPOINT}orders/{item_id}").json()
        REDIS.set(item_id, json.dumps(response))
    return response


@app.get("/orders")
def get_orders():
    response = requests.get(Config.SHIPMENTS_ENDPOINT +
                            "orders").json()
    return response


@app.post("/orders")
def post_form(order: Order):
    order = {
        'item_id': order.item_id,
        'price': order.price,
        'quantity': order.quantity
    }
    response = requests.post(Config.PAYMENTS_ENDPOINT +
                             "payments", data=json.dumps(order)).json()
    return response


if __name__ == "__main__":
    uvicorn.run(app)
