import time
from machine import Pin  # type: ignore

power = Pin(21, Pin.OUT)
power.on()
motor = Pin(22, Pin.OUT)

def main():
    
    file = open("data.csv", "w")
    for _ in range(20):
        motor.on()
        time.sleep(1.5)
        motor.off()
        time.sleep(1.5)

    file.close()

main()