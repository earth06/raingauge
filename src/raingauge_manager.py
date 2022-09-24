from re import I
import textwrap
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
        """
        self.DBFILEPATH="../data/weather.db"
        self.SWITCH_PIN=4
        self.timefmt="%Y-%m-%dT%H:%M:%S"
        self.time_old=time.time()
        self.conn=None

    def set_gpio(self):
        """setup gpio for rain observation
        """
        self.pi=pigpio.pi()
        self.pi.set_mode(self.SWITCH_PIN, pigpio.INPUT)
        self.pi.set_pull_up_down(self.SWITCH_PIN, pigpio.PUD_OFF)

    def set_db(self):
        """connect to database file"""
        self.conn=sqlite3.connect(self.DBFILEPATH)
        self.cursor=self.conn.cursor()        

    def record_rain_mass(self, gpio, level, tick):
        """callback function to record bucket tipping count to db
        """
        #avoid chattering
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
        """observing rain"""
        state = self.pi.callback(self.SWITCH_PIN, pigpio.RISING_EDGE, self.record_rain_mass)
        try:
            while True:
                pass
        except Exception:
            self.conn.close()
            self.pi.stop()

    def clear_raw_rain_data(self):
        """delete raw observed data more than 1 week before from db
        """
        before_1week=datetime.now() - timedelta(days=7)
        before_1week=before_1week.strftime(self.timefmt)
        sql="DELETE FROM raw_rain_data WHERE date_time <= ?"
        self.cursor.execute(sql, (before_1week,))
        self.conn.commit()

    def clear_all_raw_rain_data(self):
        """delete all raw observed data from db
        """
        sql="DELETE FROM raw_rain_data"
        self.cursor.execute(sql)
        self.conn.commit()

    def get_precipitation(self, begin=None, end=None, freq="H"):
        """calc precip mass per custom frequency
        
        Args:
            begin(str): begin of sample data,('YYYY-MM-DD hh:mm:ss')
            end(str): end of sample data, ('YYYY-MM-DD hh:mm:ss')
            freq(str): frequency of sample,{"H","D"...,default,}
        Return:
            pd.DataFrame: resampled precipitation dataframe
            
        """
        if begin is None:
            begin=(datetime.now() - timedelta(days=3)).strftime(self.timefmt)
        if end is None:
            end=datetime.now().strftime(self.timefmt)
        sql=f"SELECT * FROM raw_rain_data WHERE date_time BETWEEN '{begin}' AND '{end}'"
        df=pd.read_sql(sql, self.conn)
        df.set_index("date_time", inplace=True)
        df.index=pd.to_datetime(df.index)
        df_resample=df.resample(freq).sum().fillna(0.0)*0.5
        return df_resample

    def __del__(self):
        if self.conn is not None:
            self.conn.close()

if __name__=="__main__":
    args_help=textwrap.dedent("""
    select runnning mode
        obs : observing rain by gpio
        get : print observed hourly precipitaion
        clear, clearall : delete old raw observed data
    """)
    parser=argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("mode",choices=["obs","get","clear","clearall"],help=args_help
    
    )
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
   
    elif args.mode=="clearall":
        observer=Raingauge()
        observer.set_db()
        observer.clear_all_raw_rain_data()
