import pymysql

class SQLUtils:
    def __init__(self, server, username, password, database, port):
        self.db = pymysql.connect(
            host = server,
            user = username,
            passwd = password,
            db = database,
            port = port
        )

        self.cursor = self.db.cursor()
    
    def query_timestamp(self):
        self.cursor.execute("SELECT timestamp FROM chat_history")
        return self.cursor.fetchall()
    
    def query_user_content(self):
        self.cursor.execute("SELECT user_content FROM chat_history")
        return self.cursor.fetchall()

    def query_bot_content(self):
        self.cursor.execute("SELECT bot_content FROM chat_history")
        return self.cursor.fetchall()
    
    def save_conversation(self, timestamp, user_content, bot_content):
        sql_query = f"INSERT INTO chat_history (timestamp, user_content, bot_content) VALUES ( '{timestamp}', '{user_content}', '{bot_content}')"
        self.cursor.execute(sql_query)
        self.db.commit()

    def close(self):
        self.db.close()

