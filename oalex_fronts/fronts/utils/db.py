import psycopg

# Database connection parameters
DB_NAME = "myuserdb"
DB_USER = "myuser"
DB_PASSWORD = "mypassword"
DB_HOST = "localhost"
DB_PORT = "5432" # Default PostgreSQL port

class DB:
    def __init__(self):
        try:
            self.conn = psycopg.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
        except psycopg.OperationalError as e:
            print(f"Unable to connect to the database: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_results(self, entity_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute(f"""SELECT id, content, valid_until FROM api_cache where entity_id = '{entity_id}'""")
        except Exception as e:
            print(f"Unable to execute query: {e}")
            return None, None, None

        records = cursor.fetchall()
        if len(records) == 0:
            return None, None, None

        result = records[0]

        return result[0], result[1], result[2]

    def insert(self, entity_id, content, valid_until):
        cursor = self.conn.cursor()
        try:
            content = str(content).replace("'", '"')
            insertStr = f"""INSERT INTO api_cache (entity_id, content, valid_until) VALUES ('{entity_id}', '{content}', '{valid_until}')"""
            cursor.execute(insertStr)
            self.conn.commit()
        except Exception as e:
            print(f"Unable to execute query: {e}")

    def remove_by_id(self, id):
        cursor = self.conn.cursor()
        try:
            cursor.execute(f"""delete from api_cache where id == {id}""")
        except Exception as e:
            print(f"Unable to execute query: {e}")
