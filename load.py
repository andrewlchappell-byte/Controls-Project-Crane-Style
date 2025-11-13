with open("main.py","w") as f: f.write("""import time
from machine import Pin  # type: ignore

power = Pin(21, Pin.OUT)
power.on()
motor = Pin(22, Pin.OUT)

def blink_forever():
    print("main: entering blink loop")
    while True:
        motor.on()
        time.sleep(3)
        motor.off()
        time.sleep(3)

blink_forever()""")

with open("boot.py","w") as f: f.write("""# boot.py""")