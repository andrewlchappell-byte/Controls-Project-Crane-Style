with open("main.py","w") as f: f.write(r"""from machine import Pin, time_pulse_us
import time

# for disturbance and outlier rejection
class Filtered:

    def __init__(self, threshold = 10, persistance = 3):

        self.threshold = threshold
        self.persistance = persistance
        self.last = None
        self.pending = None
        self.count = 0
        self.values = []

    def filter(self, value):

        # base case:
        if self.last == None:

            self.last = value

        # edge case
        if value is None:
            return
        
        # the point is an outlier
        if abs(value - self.last) > self.threshold:

            # restart of the outlier is even bigger
            if self.pending is None or abs(value - self.pending) > self.threshold:
                self.pending = value
                self.count = 1
            
            # the outlier seems to be staying
            else:
                self.count += 1

            # the outlier has stayed long enough to be accepted
            if self.count >= self.persistance:
                self.last  = self.pending
                self.pending = None
                self.count = 0

        # no outlier
        else:
            self.last = value
            self.pending = None
            self.count = 0

        self.values.append(self.last)

    def __getitem__(self, key):
        return self.values[key]
        
TIMES = []
SETPOINTS = []
WINCH_DISTANCES = Filtered(persistance = 3, threshold = 15)
NORTH_DISTANCES = Filtered(persistance = 3, threshold = 15)
SOUTH_DISTANCES = Filtered(persistance = 3, threshold = 15)
WINCH_ACTIONS = []
SIDE_ACTIONS = []

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

def test_sensors():

    # test winch sensor
    winch_distance = get_distance_cm(winch_sensor_trig, winch_sensor_echo)
    assert winch_distance is not None, "Winch sensor failed"
    print("Winch sensor passed")

    time.sleep(1)

    # test north sensor
    north_distance = get_distance_cm(north_sensor_trig, north_sensor_echo)
    assert north_distance is not None, "North sensor failed"
    print("North sensor passed")
    
    time.sleep(1)

    # test south sensor
    south_distance = get_distance_cm(south_sensor_trig, south_sensor_echo)
    assert south_distance is not None, "South sensor failed"
    print("South sensor passed")

def get_distance_cm(trig_pin: Pin, echo_pin: Pin, timeout_us=30000):

    # Send 10us trigger pulse
    trig_pin.value(0)
    time.sleep_us(2)
    trig_pin.value(1)
    time.sleep_us(10)
    trig_pin.value(0)

    pulse = time_pulse_us(echo_pin, 1, timeout_us)

    if pulse <= 0:
        # print(pulse)
        return None

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

def side_stop():
    side_motor_power.off()
    side_motor_north.off()
    side_motor_south.off()

def move_north():
    side_motor_south.off()
    side_motor_power.on()
    side_motor_north.on()

def move_south():
    side_motor_north.off()
    side_motor_power.on()
    side_motor_south.on()

def sample(winch_distance, north_distance, south_distance, setpoint = None, side_motor = 0):
    
    TIMES.append(time.ticks_ms())
    SETPOINTS.append(setpoint)
    WINCH_DISTANCES.filter(winch_distance)
    NORTH_DISTANCES.filter(north_distance)
    SOUTH_DISTANCES.filter(south_distance)
    SIDE_ACTIONS.append(side_motor)

def to_setpoint(setpoint):

    setpoint = max(10, min(setpoint, 50))

    while True:
        # wait a sec
        time.sleep(0.1)

        # record one sample per loop
        winch_distance = get_distance_cm(winch_sensor_trig, winch_sensor_echo)
        north_distance = get_distance_cm(north_sensor_trig, north_sensor_echo)
        south_distance = get_distance_cm(south_sensor_trig, south_sensor_echo)
        
        sample(winch_distance, north_distance, south_distance, setpoint)
        if winch_distance is not None and north_distance is not None and south_distance is not None:

            # timeout/no reading: stop motor and log action 0
            if winch_distance <= 0:
                winch_stop()
                WINCH_ACTIONS.append("0")
                # short delay then retry
                time.sleep(0.1)
                continue

            error = setpoint - winch_distance

            if error > 0.25:  # too far
                winch_up()
                WINCH_ACTIONS.append("1")

            elif error < -0.25:  # too close
                winch_down()
                WINCH_ACTIONS.append("-1")

            else:  # at setpoint
                winch_stop()
                WINCH_ACTIONS.append("0")
                break
        
def pass_obstacle(load_height = 7, threshold = 0):

    while True:
        # wait a sec
        time.sleep(0.1)

        # measure distances
        winch_distance = get_distance_cm(winch_sensor_trig, winch_sensor_echo)
        north_distance = get_distance_cm(north_sensor_trig, north_sensor_echo)
        south_distance = get_distance_cm(south_sensor_trig, south_sensor_echo)

        # there is a tall obstacle
        found_obstacle = False
        on_obstacle = False
        if north_distance is not None and winch_distance is not None and south_distance is not None:

            if north_distance + threshold + load_height < winch_distance and not found_obstacle:
                print("Obstacle: ", north_distance, south_distance, winch_distance)
                sample(winch_distance, north_distance, south_distance, None, 0)
                side_stop()
                to_setpoint(north_distance - load_height - threshold)
                found_obstacle = True

            # there is a valley / we passed over the obstacle
            elif south_distance - threshold - load_height < winch_distance and found_obstacle:
                on_obstacle = True
            
            elif south_distance - threshold - load_height > winch_distance and on_obstacle:
                print("Valley: ", north_distance, south_distance, winch_distance)
                sample(winch_distance, north_distance, south_distance, None, 0)
                side_stop()
                to_setpoint(south_distance - load_height - threshold)

                # exit
                break

            # move forward
            else:
                print("moving forward")
                sample(winch_distance, north_distance, south_distance, None, 1)
                move_south()

def main():
    
    test_sensors()
    winch_stop()
    side_stop()

    try:
        # move_north()
        # time.sleep(1)
        # side_stop()
        to_setpoint(45)
        pass_obstacle()

    finally:
        string = "Time,Setpoint,Winch Distance,North Distance,South Distance,Winch Action,Side Action\n"
        stringy = []

        def safe_get(container, i):
            try:
                # Filtered implements __getitem__ to access values
                return container[i]
            except Exception:
                try:
                    return container.values[i]
                except Exception:
                    return ""

        # SMOOTH_TIMES = smooth_times(TIMES)

        n = len(TIMES)
        for i in range(n):
            row = [
                safe_get(TIMES, i),
                safe_get(SETPOINTS, i),
                safe_get(WINCH_DISTANCES, i),
                safe_get(NORTH_DISTANCES, i),
                safe_get(SOUTH_DISTANCES, i),
                safe_get(WINCH_ACTIONS, i),
                safe_get(SIDE_ACTIONS, i)
            ]
            stringy.append(",".join(map(str, row)))

        string += "\n".join(stringy)

        with open("data.csv", "w") as file:
            file.write(string)

if __name__ == "__main__":

    main()""")

with open("boot.py","w") as f: f.write(r"""# boot.py
""")