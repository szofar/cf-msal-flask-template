"""Database methods"""


from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


def update_visits(db):
    """Updates the number of visits to the dashboard
        :param db: the database client connection
        """
    db["__universal__"].update_one(
        {"num_visits": {"$exists": True}},
        {"$inc": {"num_visits": 1}},
        upsert=True
    )
    return get_visits(db)


def get_visits(db):
    """Updates the number of visits to the dashboard
        :param db: the database client connection
        """
    try:
        return db["__universal__"].find_one({"num_visits": {"$exists": True}})["num_visits"]
    except KeyError:
        return 0


def ensure_exists(product_step, db, regions=None, simode_roots=None):
    if regions is None:
        regions = []
    if simode_roots is None:
        simode_roots = []
    db["__products__"].update_one(
        {"name": product_step},
        {"$set": {
            "name": product_step,
            "regions": regions,
            "simode_roots": simode_roots
        }},
        upsert=True
    )


class OpenMongoClientConnection:
    """Allows opening a MongoClient connection using "with", to streamline closing the connection"""
    def __init__(self, connection_string, tls_allow_invalid_certificates: bool = True):
        self.__connection_string = connection_string
        self.__tls_allow_invalid_certificates = tls_allow_invalid_certificates

    def __enter__(self):
        self.client = MongoClient(
            self.__connection_string, tlsAllowInvalidCertificates=self.__tls_allow_invalid_certificates)
        for n in range(3):
            try:
                self.client.admin.command("ping")
                return self.client
            except ConnectionFailure:
                print(f"Failed to connect to the database!")
                if n != 2:
                    print(f"Launching attempt {n + 2}")
                    continue
                break

        self.client = None
        raise ConnectionError("Connection failure detected. Database may be offline or you do not have access...")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
