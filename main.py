from machine import Pin, PWM, time_pulse_us
import time

# -------------------------
# Ultrasonic pins
# -------------------------
TRIG_PIN = 27
ECHO_PIN = 26

trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

# -------------------------
# Winch motor control pins
# -------------------------
winch_power = PWM(Pin(23), freq=1000)  # PWM enable
winch_up    = Pin(22, Pin.OUT)
winch_down  = Pin(21, Pin.OUT)

# -------------------------
# Motor control helpers
# -------------------------
def winch_stop():
    winch_up.value(0)
    winch_down.value(0)
    winch_power.duty(0)

def winch_raise(speed=800):
    winch_up.value(1)
    winch_down.value(0)
    winch_power.duty(speed)

def winch_lower(speed=800):
    winch_up.value(0)
    winch_down.value(1)
    winch_power.duty(speed)

# -------------------------
# Distance measurement (cm)
# -------------------------
def get_distance():
    trig.value(0)
    time.sleep_us(2)

    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    pulse = time_pulse_us(echo, 1, 30000)

    if pulse <= 0:
        return None

    return (pulse / 2) / 29.1  # cm


# -------------------------
# CSV Logging Setup
# -------------------------
CSV_FILENAME = "distance_log.csv"

# Create/overwrite file and add header
with open(CSV_FILENAME, "w") as f:
    f.write("time_s,distance_cm\n")

def log_distance(timestamp, distance):
    """Append one line to CSV."""
    with open(CSV_FILENAME, "a") as f:
        f.write(timestamp)
        f.write(",")
        f.write(float(distance))
        file.write("\n")


# -------------------------
# Step test parameters
# -------------------------
STEP_TARGETS = [20, 30, 10]  # cm
SETTLE_TIME  = 5      # seconds
TOLERANCE    = 1.0    # cm


# -------------------------
# Main step test loop
# -------------------------
if not get_distance():
    quit()
    1 / 0


for target in STEP_TARGETS:
    print("\n--- New Step Target:", target, "cm ---")

    reached_target = False
    step_start_time = None

    while True:
        dist = get_distance()
        now = time.time()

        print("Distance:", dist, "cm")

        # Log distance to CSV
        log_distance(now, dist)

        # --- Movement control ---
        #if dist is None:
            #print("No echo — stopping motor")
            #winch_stop()
            #continue

        if dist > target + TOLERANCE:
            print("→ Raising load")
            winch_raise(700)

        elif dist < target - TOLERANCE:
            print("→ Lowering load")
            winch_lower(700)

        else:
            if not reached_target:
                print("Target reached — holding")
                reached_target = True
                step_start_time = now

            winch_stop()

        if reached_target and (now - step_start_time) >= SETTLE_TIME:
            print("Step complete.")
            winch_stop()

        time.sleep(0.1)

# End
print("\nStep test finished.")
winch_stop()
