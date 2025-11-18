with open("main.py","w") as f: f.write(r"""from machine import Pin, time_pulse_us
import time

TIMES = []
SETPOINTS = []
DISTANCES = []
ACTIONS = []

winch_sensor_trig = Pin(27, Pin.OUT)
winch_sensor_echo = Pin(26, Pin.IN)

winch_motor_power = Pin(23, Pin.OUT)
winch_motor_up = Pin(21, Pin.OUT)
winch_motor_down = Pin(22, Pin.OUT)

def get_distance_cm(trig_pin:Pin, echo_pin:Pin, timeout_us=30000):

    # Send 10us trigger pulse
    trig_pin.value(0)
    time.sleep_us(2)
    trig_pin.value(1)
    time.sleep_us(10)
    trig_pin.value(0)

    pulse = time_pulse_us(echo_pin, 1, timeout_us)

    if pulse <= 0:
        return None
    
    return (pulse / 2) / 29.1 # cm

def winch_up():

    winch_motor_down.off()
    winch_motor_power.on()
    winch_motor_up.on()

def winch_down():

    winch_motor_up.off()
    winch_motor_power.on()
    winch_motor_down.on()

def winch_stop():

    winch_motor_power.off()
    winch_motor_up.off()
    winch_motor_down.off()

def to_setpoint(setpoint):

    while True:

        time.sleep(0.1)
        distance = get_distance_cm(winch_sensor_trig, winch_sensor_echo)
        print(f"\r{distance}", end = "")

        # add values
        TIMES.append(str(time.time()))
        SETPOINTS.append(str(setpoint))
        DISTANCES.append(str(distance))

        if distance is None:
            winch_stop()
            ACTIONS.append("0")
        
        else:
            error = setpoint - distance
    
            if error > 0.25: # too far
                winch_up()
                ACTIONS.append("1")

            elif error < -0.25: # too close
                winch_down()
                ACTIONS.append("-1")

            else: # at setpoint
                winch_stop()
                ACTIONS.append("0")
                break
        
def main():
    
    try:
        print("Looking for 20.")
        to_setpoint(20)
        time.sleep(3)
        print("\nLooking for 30.")
        to_setpoint(30)
        time.sleep(3)
        print("\nLooking for 10.")
        to_setpoint(10)
        time.sleep(3)

    finally:
        with open("data.csv", "w") as file:
            file.write("Time,Setpoint,Distance,Action\n")
            
            for i in range(len(TIMES)):
                file.write(",".join((TIMES[i],SETPOINTS[i],DISTANCES[i],ACTIONS[i],"\n")))

if __name__ == "__main__":

    main()""")

with open("boot.py","w") as f: f.write(r"""# boot.py
""")