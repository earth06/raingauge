import pigpio


SWITCH_PIN = 4
pi = pigpio.pi()

pi.set_mode(SWITCH_PIN, pigpio.INPUT)
pi.set_pull_up_down(SWITCH_PIN, pigpio.PUD_OFF)


def is_switch_on(gpio, level, tick):
    print(gpio, level, tick)


chck = pi.callback(SWITCH_PIN, pigpio.RISING_EDGE, is_switch_on)

try:
    while True:
        pass
except Exception:
    pass
