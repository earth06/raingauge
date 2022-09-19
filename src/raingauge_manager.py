import pandas as pd
import sqlite3


class Raingauge():
    
    def __init__(self):
        """
        dbとのコネクション
        """
        self.DBFILEPATH="../data/weather.db"
        self.conn=sqlite3.connect(self.DBFILEPATH)
        pass

    def clean_rawdata(self):
        """
        雨量観測の生データの1週間より前を削除する
        """
        pass

    def get_precipitation(self, begin="2022-01-01 00:00:00", end="2022-01-01 23:00:00", freq="H"):
        """
        rawdataから任意の期間の降水量を求める
        """
        pass

    def insert_precipitation(self, df):
        """時間降水量テーブルにデータを登録"""
        pass


