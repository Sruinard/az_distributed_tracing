import os
import dotenv

dotenv.load_dotenv()


class Config:
    APIM_ENDPOINT = os.environ.get("APIM_ENDPOINT")
    APPINSIGHTS_CONNECTION_STRING = os.environ.get(
        "APPINSIGHTS_CONNECTION_STRING")
