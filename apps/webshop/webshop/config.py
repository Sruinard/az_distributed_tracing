import os
import dotenv

dotenv.load_dotenv()


class Config:
    REDIS_HOST = os.environ.get("REDIS_HOST")
    REDIS_PASS = os.environ.get("REDIS_PASS", None)
    REDIS_PORT = int(os.environ.get("REDIS_PORT"))
    PAYMENTS_ENDPOINT = os.environ.get("PAYMENTS_ENDPOINT")
    SHIPMENTS_ENDPOINT = os.environ.get("SHIPMENTS_ENDPOINT")
    APPINSIGHTS_CONNECTION_STRING = os.environ.get(
        "APPINSIGHTS_CONNECTION_STRING")
