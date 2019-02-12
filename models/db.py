import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import peewee
from playhouse.migrate import *


class DB(object):
    """
    初始化DataBase
    """

    @classmethod
    def initDB(cls):

        dbPath = '{}/models/app.db'.format(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db = peewee.SqliteDatabase(dbPath)
        return db

    @classmethod
    def initMigrator(cls):
        db = cls.initDB()
        migrator = SqliteMigrator(db)
        return migrator
