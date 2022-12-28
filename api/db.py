from neo4j import GraphDatabase


class Db:
    def __init__(self):
        self.driver = None

    def initialize_driver(self, uri, name, passwd):
        self.driver = GraphDatabase.driver(uri, auth=(name, passwd))
        self.driver.verify_connectivity()

