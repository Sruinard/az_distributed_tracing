import os
import dotenv

dotenv.load_dotenv()


class Config:
    ACCOUNT_KEY = os.environ.get("ACCOUNT_KEY")
    ACCOUNT_URI = os.environ.get("ACCOUNT_URI")
    APPINSIGHTS_CONNECTION_STRING = os.environ.get(
        "APPINSIGHTS_CONNECTION_STRING")
