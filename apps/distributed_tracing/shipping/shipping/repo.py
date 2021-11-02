from azure.cosmos import CosmosClient
from shipping.config import Config


class CosmosRepo:
    DATABASE_NAME = "webshop"
    CONTAINER_NAME = "orders"

    def __init__(self, cosmos_connection_config: Config = Config()) -> None:
        super().__init__()

        # Create the cosmos client
        self.client = CosmosClient(cosmos_connection_config.ACCOUNT_URI,
                                   credential=cosmos_connection_config.ACCOUNT_KEY)
        self.database = self.client.get_database_client(self.DATABASE_NAME)
        self.container = self.database.get_container_client(
            self.CONTAINER_NAME)

    def add(self, order):
        placed_order = self.container.upsert_item(
            order.dict()
        )
        return placed_order

    def get_all(self):
        orders = list(self.container.query_items(
            query="SELECT * FROM r",
            enable_cross_partition_query=True
        ))
        return orders
