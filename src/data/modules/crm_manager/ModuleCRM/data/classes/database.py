# Library import
import sqlite3
import time

# Classes definition
class DataBase:
    def __init__(self, resource_root: str) -> None:
        # Property definition
        self.database_file = ("Call log [%D-%M-%Y]", "db")

        # Property assigment
        self.resource_root = resource_root

    # Private methods
    pass