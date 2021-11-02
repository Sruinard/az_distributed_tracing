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
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from webshop.config import Config
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates/")
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
    resource=Resource.create({SERVICE_NAME: "webshop"})
))
tracer = trace.get_tracer(__name__)


@app.on_event("startup")
def startup_event():
    # This line causes your calls made with the requests library to be tracked.
    RequestsInstrumentor().instrument()
    span_processor = BatchSpanProcessor(
        AzureMonitorTraceExporter.from_connection_string(
            Config.APPINSIGHTS_CONNECTION_STRING
        )
    )
    trace.get_tracer_provider().add_span_processor(span_processor)

    RequestsInstrumentor().instrument()
    FastAPIInstrumentor.instrument_app(
        app, tracer_provider=trace.get_tracer_provider())


@app.get("/")
async def get():
    return "Distributed tracing"


@app.get("/orders")
def post_form(request: Request):
    return templates.TemplateResponse('form.html', context={'request': request})


@app.post("/orders")
def post_form(request: Request, price: int = Form(...), item_id: int = Form(...), quantity: int = Form(...)):
    order = {
        'item_id': item_id,
        'price': price,
        'quantity': quantity
    }
    response = requests.post(Config.APIM_ENDPOINT +
                             "payments", data=json.dumps(order)).json()

    return templates.TemplateResponse('form.html', context={'request': request, 'price': price, 'item_id': response.get('item_id'), 'quantity': quantity})


if __name__ == "__main__":
    uvicorn.run(app)
