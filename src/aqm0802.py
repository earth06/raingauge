# -*- coding: utf-8 -*-
import smbus
import pigpio
import sys
from time import sleep
class AQM0802:
    
    def __init__(self):
        self.bus = smbus.SMBus(1)
        self.address_aqm0802a = 0x3e
        self.register_setting = 0x00
        self.register_display = 0x40

        self.chars_per_line = 8
        self.display_lines = 2
        self.display_chars = self.chars_per_line*self.display_lines

        self.position = 0
        self.line = 0
    
    def set_gpio(self, pi:pigpio.pi, gpio:int=17):
        self.LED_GPIO_PIN=gpio
        self.pi=pi
        pi.set_mode(self.LED_GPIO_PIN, pigpio.OUTPUT)
        return 0
    
    def light_on(self):
        self.pi.write(self.LED_GPIO_PIN,1)
    
    def light_off(self):
        self.pi.write(self.LED_GPIO_PIN,0)

    def setup_aqm0802a(self):
        trials = 5
        for i in range(trials):
            try:
                self.bus.write_i2c_block_data(self.address_aqm0802a, self.register_setting, [0x38, 0x39, 0x14, 0x70, 0x56, 0x6c])
                sleep(0.2)
                self.bus.write_i2c_block_data(self.address_aqm0802a, self.register_setting, [0x38, 0x0d, 0x01])
                sleep(0.001)
                break
            except IOError:
                if i==trials-1:
                    sys.exit()

    def clear(self):
        self.position = 0
        self.line = 0
        self.bus.write_byte_data(self.address_aqm0802a, self.register_setting, 0x01)
        sleep(0.001)

    def newline(self):
        if self.line == self.display_lines-1:
            self.clear()
        else:
            self.line += 1
            self.position = self.chars_per_line*self.line
            self.bus.write_byte_data(self.address_aqm0802a, self.register_setting, 0xc0)
            sleep(0.001)

    def write_string(self,s):
        for c in list(s):
            self.write_char(ord(c))

    def write_char(self,c):
        byte_data = self.check_writable(c)
        if self.position == self.display_chars:
            self.clear()
        elif self.position == self.chars_per_line*(self.line+1):
            self.newline()
        self.bus.write_byte_data(self.address_aqm0802a, self.register_display, byte_data)
        self.position += 1 
    
    def check_writable(self,c):
        if c >= 0x20 and c <= 0x7d :
            return c
        else:
            return 0x20 # 空白文字

if __name__=="__main__":
    aqm0802=AQM0802()
    aqm0802.setup_aqm0802a()

    if len(sys.argv)==1:
        aqm0802.write_string('Hello World')
    else:
        aqm0802.write_string(sys.argv[1])
