with open("main.py","w") as f: f.write("""import time
from machine import Pin  # type: ignore

led = Pin(2, Pin.OUT)

def blink_forever():
    print("main: entering blink loop")
    while True:
        led.on()
        time.sleep(0.1)
        led.off()
        time.sleep(0.1)

blink_forever()""")

with open("boot.py","w") as f: f.write("""# boot.py""")