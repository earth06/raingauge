import time
from datetime import datetime
from datetime import timedelta
import argparse

from raingauge_manager import Raingauge
from aqm0802 import AQM0802
import pigpio

class RaingaugeLCD(Raingauge):

    def __init__(self):
        super().__init__()
        self.COUNT=0
        self.COUNT_RESET_PIN=27
        self.LCD_LED_PIN=17
        self.last_count_reset_time=time.time()
        self.aqm0802=AQM0802()
        self.aqm0802.setup_aqm0802a()

    def set_gpio(self):
        super().set_gpio()
        #reset button
        self.pi.set_mode(self.COUNT_RESET_PIN, pigpio.INPUT)
        self.pi.set_pull_up_down(self.COUNT_RESET_PIN, pigpio.PUD_DOWN)

        #LED button
        self.aqm0802.set_gpio(self.pi, self.LCD_LED_PIN)


    def record_rain_mass(self, gpio, level, tick):
        self.COUNT+=1
        precip=self.COUNT*0.5
        s_precip=f"{precip:.1f}"
        lcdlabel=f"precip: {s_precip:>6}mm"
        self.aqm0802.write_string(lcdlabel)
        return super().record_rain_mass(gpio, level, tick)
    
    def reset_counter(self,gpio, level, tick):
        """callback function to reset LCD counter
        """
        time_now=time.time()
        diff= time_now -self.last_count_reset_time
        if diff <=1:
            return 0
        self.COUNT=0
        return 0
    def start_rain_observation_with_counter(self):
        state2=self.pi.callback(self.COUNT_RESET_PIN, pigpio.RISING_EDGE, self.reset_counter)
        super().start_rain_observation()
    
    def __del__(self):
        self.aqm0802.clear()
        return super().__del__()

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--led_on", action="store_true")
    args=parser.parse_args()
    observer=Raingauge()
    observer.set_gpio()
    if args.led_on:
        observer.aqm0802.light_on()
    observer.start_rain_observation()