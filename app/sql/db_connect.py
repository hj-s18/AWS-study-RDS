import pymysql

class DBConnect:
    @classmethod
    def get_db(self):
        return pymysql.connect(
            user="root",
            passwd="ssafy",
            host="127.0.0.1",
            db="mood_journal_project",
            charset="utf8",
            autocommit=True,
        )