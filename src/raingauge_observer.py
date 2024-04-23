import time
from datetime import datetime
import argparse
import subprocess

from raingauge_manager import Raingauge
from aqm0802 import AQM0802
import pigpio

class RaingaugeLCD(Raingauge):

    def __init__(self):
        super().__init__()
        self.COUNT=0
        self.COUNT_RESET_PIN=27
        self.SHUTDOWN_PIN=21
        self.LCD_LED_PIN=17
        self.last_count_reset_time=time.time()
        self.init_lcd_label=f"precip: {0.0:>6}mm"
        self.aqm0802=AQM0802()
        self.aqm0802.setup_aqm0802a()
        self.aqm0802.clear()
        self.aqm0802.write_string(">ready---")

    def set_gpio(self):
        super().set_gpio()
        #reset button
        self.pi.set_mode(self.COUNT_RESET_PIN, pigpio.INPUT)
        self.pi.set_pull_up_down(self.COUNT_RESET_PIN, pigpio.PUD_DOWN)

        #LED button
        self.aqm0802.set_gpio(self.pi, self.LCD_LED_PIN)

        #shutdown button
        self.pi.set_mode(self.SHUTDOWN_PIN, pigpio.INPUT)
        self.pi.set_pull_up_down(self.SHUTDOWN_PIN, pigpio.PUD_DOWN)

    def record_rain_mass(self, gpio, level, tick):
        is_chat=super().record_rain_mass(gpio, level, tick)
        if is_chat:
            return 1
        self.COUNT+=1
        precip=self.COUNT*0.5
        s_precip=f"{precip:.1f}"
        lcdlabel=f"precip: {s_precip:>6}mm"
        self.aqm0802.write_string(lcdlabel)
        return 0
    
    def reset_counter(self,gpio, level, tick):
        """callback function to reset LCD counter
        """
        time_now=time.time()
        diff= time_now -self.last_count_reset_time
        if diff <=1:
            return 0
        self.COUNT=0
        self.aqm0802.clear()
        self.aqm0802.write_string(self.init_lcd_label)
        self.last_count_reset_time=time_now
        return 0

    def shutdown(self, gpio, level, tick):
        time_now=datetime.now()
        self.aqm0802.clear()
        self.aqm0802.write_string("shutdown @"+time_now.strftime("%H:%M"))
        res=subprocess.call('sudo /usr/sbin/shutdown +1', shell=True)
        exit()

    def start_rain_observation_with_counter(self):
        state2=self.pi.callback(self.COUNT_RESET_PIN, pigpio.RISING_EDGE, self.reset_counter)
        state3=self.pi.callback(self.SHUTDOWN_PIN, pigpio.RISING_EDGE, self.shutdown)
        super().start_rain_observation()
    
    def __del__(self):
        self.aqm0802.clear()
        return super().__del__()

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--led_on", action="store_true")
    args=parser.parse_args()
    observer=RaingaugeLCD()
    observer.set_gpio()
    if args.led_on:
        observer.aqm0802.light_on()
    observer.start_rain_observation_with_counter()
