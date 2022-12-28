import unittest
from api.db import Db

class TestConnection(unittest.TestCase):
    def test_db(self):
        uri = "bolt://localhost:7687"
        name = "neo4j"
        passwd = "xxx"
        db = Db()

        try:
            db.initialize_driver(uri, name, passwd)
            connected = True
        except:
            connected = False

        self.assertEqual(True, connected)

if __name__ == '__main__':
    unittest.main()
