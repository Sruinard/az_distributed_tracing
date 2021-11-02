import uvicorn
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (BatchSpanProcessor,
                                            ConsoleSpanExporter,
                                            SimpleSpanProcessor)

import shipping.repo as repo
from shipping.models import Order
from shipping.config import Config

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

trace.set_tracer_provider(TracerProvider(
    resource=Resource.create({SERVICE_NAME: "shipments"})
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

    # trace.get_tracer_provider().add_span_processor(
    #     SimpleSpanProcessor(ConsoleSpanExporter())
    # )
    RequestsInstrumentor().instrument()
    FastAPIInstrumentor.instrument_app(
        app, tracer_provider=trace.get_tracer_provider())


@app.get("/")
async def get():
    return "Distributed tracing"


@app.get("/orders")
async def create_order():
    order_repo = repo.CosmosRepo()
    orders = order_repo.get_all()
    return orders


@app.post("/orders")
async def create_order(order: Order):
    order_repo = repo.CosmosRepo()
    placed_order = order_repo.add(order)
    return placed_order


if __name__ == "__main__":
    uvicorn.run(app)
