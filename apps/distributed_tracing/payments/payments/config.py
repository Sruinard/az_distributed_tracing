import os
import dotenv

dotenv.load_dotenv()

class Config:
    shipping_endpoint = os.environ.get("SHIPPING_ENDPOINT")
    appinsights_connection_string = os.environ.get("APPINSIGHTS_CONNECTION_STRING")
