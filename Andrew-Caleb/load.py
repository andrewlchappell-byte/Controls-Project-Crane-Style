with open("main.py","w") as f: f.write(r"""from machine import Pin, time_pulse_us
import time

TIMES = []
SETPOINTS = []
WINCH_DISTANCES = []
NORTH_DISTANCES = []
SOUTH_DISTANCES = []
ACTIONS = []

# sensors
winch_sensor_trig = Pin(27, Pin.OUT)
winch_sensor_echo = Pin(26, Pin.IN)

north_sensor_trig = Pin(25, Pin.OUT)
north_sensor_echo = Pin(33, Pin.IN)

south_sensor_trig = Pin(12, Pin.OUT)
south_sensor_echo = Pin(14, Pin.IN)

# motors
winch_motor_power = Pin(23, Pin.OUT)
winch_motor_up = Pin(21, Pin.OUT)
winch_motor_down = Pin(22, Pin.OUT)

side_motor_power = Pin(5, Pin.OUT)
side_motor_north = Pin(18, Pin.OUT)
side_motor_south = Pin(19, Pin.OUT)

def get_distance_cm(trig_pin: Pin, echo_pin: Pin, timeout_us=30000):
    # Send 10us trigger pulse
    trig_pin.value(0)
    time.sleep_us(2)
    trig_pin.value(1)
    time.sleep_us(10)
    trig_pin.value(0)

    pulse = time_pulse_us(echo_pin, 1, timeout_us)

    if pulse <= 0:
        return 0

    return (pulse / 2) / 29.1  # cm

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
        distance = float(get_distance_cm(winch_sensor_trig, winch_sensor_echo))
        # try:
        #     old = WINCH_DISTANCES[-1]
        # except:
        #     old = distance
        # alpha = 0.1
        # distance = alpha * old + (1 - alpha) * distance

        # record one sample per loop
        TIMES.append(str(time.time()))
        SETPOINTS.append(str(setpoint))
        WINCH_DISTANCES.append(str(distance))
        NORTH_DISTANCES.append(str(get_distance_cm(north_sensor_trig, north_sensor_echo)))
        SOUTH_DISTANCES.append(str(get_distance_cm(south_sensor_trig, south_sensor_echo)))

        if distance is None:
            # timeout/no reading: stop motor and log action 0
            winch_stop()
            ACTIONS.append("0")
            # short delay then retry
            time.sleep(0.1)
            continue

        error = setpoint - distance

        if error > 0.25:  # too far
            winch_up()
            ACTIONS.append("1")

        elif error < -0.25:  # too close
            winch_down()
            ACTIONS.append("-1")

        else:  # at setpoint
            winch_stop()
            ACTIONS.append("0")
            break
        
def main():
    
    try:
        print("Looking for 20.")
        for _ in range(3):
            time.sleep(2)
            to_setpoint(min(50, float(get_distance_cm(south_sensor_trig, south_sensor_echo))) - 5)
        to_setpoint(10)

    finally:
        string = "Time,Setpoint,Winch Distance,North Distance,South Distance,Action\n"
        stringy = []

        for i in range(len(TIMES)):
            stringy.append(",".join((TIMES[i],SETPOINTS[i],WINCH_DISTANCES[i],NORTH_DISTANCES[i],SOUTH_DISTANCES[i],ACTIONS[i])))

        string += "\n".join(stringy)

        with open("data.csv", "w") as file:
            file.write(string)

if __name__ == "__main__":

    main()""")

with open("boot.py","w") as f: f.write(r"""# boot.py
""")