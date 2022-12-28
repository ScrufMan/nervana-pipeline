from api.db import Db

def index_name(full_name, document, db):
    with db.driver.session() as session:

        query = """MERGE (p:Person {{name: "{0}"}})
        MERGE (doc:Document {{name: "{1}"}})
        MERGE (doc)-[:CONTAINS]->(p)""".format(full_name, document)

        session.run(query)

def index_mail_name(full_name, mail, db):
    with db.driver.session() as session:

        query = """MERGE (p:Person {{name: "{0}"}})
        MERGE (mail:Email {{adress: "{1}"}})
        MERGE (p)-[:has]->(mail)""".format(full_name, mail)

        session.run(query)

db = Db()
db.initialize_driver("bolt://localhost:7687", "neo4j", "xxx")

index_name("Jozko Mrkvicka", "tajne.txt", db)
index_name("Milan Jan Bezmapy", "tajne.txt", db)
index_mail_name("Jozko Mrkvicka", "mrkviacka@gmail.com", db)