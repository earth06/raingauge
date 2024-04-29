import subprocess
import pigpio
from time import sleep, time

LIGHT_BUTTON_PIN = 5
SHUTDOWN_BUTTON_PIN = 6
GATE_PIN = 20


class DeskLight:
    def __init__(self):
        self.LIGHT_BUTTON_PIN = LIGHT_BUTTON_PIN
        self.SHUTDOWN_BUTTON_PIN = SHUTDOWN_BUTTON_PIN
        self.GATE_PIN = GATE_PIN
        self.pi = pigpio.pi()

        self.pi.set_mode(self.LIGHT_BUTTON_PIN, pigpio.INPUT)
        self.pi.set_pull_up_down(self.LIGHT_BUTTON_PIN, pigpio.PUD_OFF)

        self.pi.set_mode(self.SHUTDOWN_BUTTON_PIN, pigpio.INPUT)
        self.pi.set_pull_up_down(self.SHUTDOWN_BUTTON_PIN, pigpio.PUD_OFF)

        self.pi.set_mode(self.GATE_PIN, pigpio.OUTPUT)
        self.last_light_button_pushtime = time()

    def shutdown(self, gpio, level, tick):
        for i in range(5):
            self.pi.write(self.GATE_PIN, pigpio.HIGH)
            sleep(0.5)
            self.pi.write(self.GATE_PIN, pigpio.LOW)
        res = subprocess.call("sudo /usr/sbin/shutdown +1", shell=True)
        exit()
        pass

    def light_on_off(self, gpio, level, tick):
        time_now = time()
        diff = time_now - self.last_light_button_pushtime
        self.last_light_button_pushtime = time_now
        if diff <= 0.25:
            return False
        # GPIOの状態を読み取る
        gate_state = self.pi.read(self.GATE_PIN)
        if gate_state == 1:
            self.pi.write(self.GATE_PIN, pigpio.LOW)
        elif gate_state == 0:
            self.pi.write(self.GATE_PIN, pigpio.HIGH)
        return True

    def run(self):
        self.pi.callback(self.SHUTDOWN_BUTTON_PIN, pigpio.RISING_EDGE, self.shutdown)
        self.pi.callback(self.LIGHT_BUTTON_PIN, pigpio.RISING_EDGE, self.light_on_off)
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            self.pi.stop()


if __name__ == "__main__":
    light = DeskLight()
    light.run()
