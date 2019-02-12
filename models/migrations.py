import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import peewee
from playhouse.migrate import *

from models.db import DB
from models.apiToken import APIToken

db = DB.initDB()
migrator = DB.initMigrator()


class TableFactory(object):
    """
    peewee table factory
    """

    @classmethod
    def createTable(cls, table):
        if not table.table_exists():
            table.create_table()
            print('Table創建成功')
        else:
            print('Table創建失敗')

    @classmethod
    def dropTable(cls, table):
        if table.table_exists():
            table.drop_table()
            print('Table刪除成功')
        else:
            print('Table刪除失敗')


class DBMigrator():
    """
    資料庫Table版本控管
    """

    @classmethod
    def migrate(cls, version):

        # version.1 - 新增table
        if version == 1:
            with db.atomic():
                TableFactory.createTable(APIToken())

        # # version.2 - 新增欄位
        # if version == 2:
        #     with db.atomic():
        #         migrate(
        #             migrator.add_column(
        #                 'user', 'notifyUrl',
        #                 peewee.CharField(
        #                     max_length=255,
        #                     null=False,
        #                     default='',
        #                     verbose_name='回調通知Url')), )


if __name__ == "__main__":
    version = 1
    DBMigrator.migrate(version)
    # pass
