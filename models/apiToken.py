"""
API Model
"""

import os, sys
import time
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import peewee
from playhouse.shortcuts import model_to_dict, dict_to_model

from models.db import DB

# 初始化peewee database
db = DB.initDB()


class BaseModel(peewee.Model):
    """
    peewee model basic
    """

    createdAt = peewee.DateTimeField(
        default=datetime.now(), verbose_name='建立時間')
    updateAt = peewee.DateTimeField(
        default=datetime.now(), verbose_name='更新時間')

    @classmethod
    def update(cls, *args, **kwargs):
        cls.updateAt = datetime.now()
        kwargs['updateAt'] = cls.updateAt
        return super(BaseModel, cls).update(*args, **kwargs)

    class Meta:
        database = db


class APIToken(BaseModel):
    """
    API Model
    """
    token = peewee.CharField(
        max_length=255,
        null=False,
        unique=True,
        verbose_name='Token值',
    )
    requestTime = peewee.IntegerField(
        null=False,
        verbose_name='請求時間',
    )


def seeder():
    """
    測試資料
    """
    _token = APIToken()
    _token.token = '12345678'
    _token.requestTime = int(time.time())
    _token.save()


if __name__ == "__main__":
    seeder()
