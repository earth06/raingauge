from re import I
import pandas as pd
import sqlite3
import pigpio
from datetime import datetime
from datetime import timedelta
import argparse
import time

class Raingauge():
    
    def __init__(self):
        """
        dbとのコネクション
        """
        self.DBFILEPATH="../data/weather.db"
        self.SWITCH_PIN=4
        self.timefmt="%Y-%m-%dT%H:%M:%S"
        self.time_old=time.time()
        pass

    def set_gpio(self):
        self.pi=pigpio.pi()
        self.pi.set_mode(self.SWITCH_PIN, pigpio.INPUT)
        self.pi.set_pull_up_down(self.SWITCH_PIN, pigpio.PUD_OFF)

    def set_db(self):
        self.conn=sqlite3.connect(self.DBFILEPATH)
        self.cursor=self.conn.cursor()        

    def record_rain_mass(self, gpio, level, tick):
        """転倒ますの転倒を検知するとcallbackされてdbに記録する
        """
        #チャタリング回避
        time_now=time.time()
        diff = time_now - self.time_old
        if diff <= 1:
            return 0
        
        conn=sqlite3.connect(self.DBFILEPATH)
        cursor=conn.cursor()
        now=datetime.now().strftime(self.timefmt)
        obs_data=(now, 1)
        sql="INSERT INTO raw_rain_data VALUES (?, ?)"
        cursor.execute(sql, obs_data)
        conn.commit()
        conn.close()
        self.time_old=time_now
        return 1

    def start_rain_observation(self):
        """降水量カウントを開始する"""
        state = self.pi.callback(self.SWITCH_PIN, pigpio.RISING_EDGE, self.record_rain_mass)
        try:
            while True:
                pass
        except Exception:
            self.conn.close()
            self.pi.stop()

    def clear_raw_rain_data(self):
        """
        雨量観測の生データの1週間より前を削除する
        """
        before_1week=datetime.now() - timedelta(days=7)
        before_1week=before_1week.strftime(self.timefmt)
        sql="DELETE FROM raw_rain_data WHERE date_time <= ?"
        self.cursor(sql, (before_1week,))

    def clear_all_raw_rain_data(self):
        sql="DELETE FROM raw_rain_data"
        self.cursor(sql)

    def get_precipitation(self, begin=None, end=None, freq="H"):
        """
        rawdataから任意の期間の降水量を求める
        """
        if begin is None:
            begin=(datetime.now() - timedelta(days=3)).strftime(self.timefmt)
        if end is None:
            end=datetime.now().strftime(self.timefmt)
        sql=f"SELECT * FROM raw_rain_date WHERE date_time BETWEEN '{begin}' AND '{end}'"
        df=pd.read_sql(sql, self.conn)
        df.set_index("date_time", inplace=True)
        df.index=pd.to_datetime(df.index)
        df_resample=df.resample(freq=freq).sum().fillna()*0.5
        return df_resample

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=["obs","get","clear","clearall"])
    args=parser.parse_args()

    if args.mode=="obs":
        observer=Raingauge()
        observer.set_gpio()
        observer.start_rain_observation()

    elif args.mode=="get":
        observer=Raingauge()
        observer.set_db()
        df=observer.get_precipitation(freq="H")
        print(df)

    elif args.mode=="clear":
        observer=Raingauge()
        observer.set_db()
        observer.clear_raw_rain_data()

    #降水量観測データを全てクリア    
    elif args.mode=="clearall":
        observer=Raingauge()
        observer.set_db()
        observer.clear_all_raw_rain_data()