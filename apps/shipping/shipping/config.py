import os
import dotenv

dotenv.load_dotenv()


class CosmosConfig:
    ACCOUNT_KEY = os.environ.get("ACCOUNT_KEY")
    ACCOUNT_URI = os.environ.get("ACCOUNT_URI")


def get_cosmos_connection_config():
    return CosmosConfig()


def get_instrumentation_key():
    return os.environ.get("APPINSIGHTS_INSTRUMENTATIONKEY")
