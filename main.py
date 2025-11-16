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

    return (pulse / 2) / 29.1   # cm

# -------------------------
# Step test parameters
# -------------------------
STEP_TARGETS = [20]   # example step distances (cm)

SETTLE_TIME  = 5       # seconds at each step target
TOLERANCE    = 1.0     # cm acceptable deviation

# -------------------------
# Main step test loop
# -------------------------

# winch lower function turns small gear clockwise
for target in STEP_TARGETS:
    print("\n--- New Step Target:", target, "cm ---")

    reached_target = False
    step_start_time = None

    while True:
        dist = get_distance()

        if dist is None:
            print("No echo — stopping for safety")
            winch_stop()
            continue

        print("Distance:", dist, "cm")

        # --- Control movement ---
        if dist > target + TOLERANCE:
            print("→ Raising load")
            winch_raise(700)

        elif dist < target - TOLERANCE:
            print("→ Lowering load")
            winch_lower(700)

        else:
            # Within target range
            if not reached_target:
                print("Target reached — holding")
                reached_target = True
                step_start_time = time.time()

            winch_stop()

        # If target reached and held long enough → move to next step
        if reached_target and (time.time() - step_start_time) >= SETTLE_TIME:
            print("Step complete. Moving to next step.")
            winch_stop()
            break

        time.sleep(0.1)

# End of step test
print("\nStep test finished.")
winch_stop()
