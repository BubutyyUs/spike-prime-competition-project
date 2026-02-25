from spike import PrimeHub, MotorPair, ColorSensor, DistanceSensor
from spike.control import wait_for_seconds

hub = PrimeHub()
drive = MotorPair('A', 'B')
color_sensor = ColorSensor('C')
distance_sensor = DistanceSensor('D')

# -----------------------------
# SPEED SETTINGS
# -----------------------------
BASE_SPEED = 30
SLOW_SPEED = 18

SLOW_DISTANCE = 25
WALL_DISTANCE = 14

# -----------------------------
# PD CONTROL CONSTANTS
# -----------------------------
KP = 1.0
KD = 0.5

drive.set_default_speed(BASE_SPEED)

# -----------------------------
# UTILITY FUNCTIONS
# -----------------------------
def clamp(value, min_value=-100, max_value=100):
return max(min_value, min(max_value, value))

def wait_for_button_press():
while not hub.left_button.is_pressed() and not hub.right_button.is_pressed():
wait_for_seconds(0.05)
wait_for_seconds(0.3)

def read_average_light(samples=10):
total = 0
for _ in range(samples):
total += color_sensor.get_reflected_light()
wait_for_seconds(0.02)
return int(total / samples)

# -----------------------------
# BLACK LINE CALIBRATION
# -----------------------------
def calibrate_black_line():
hub.light_matrix.write("B") # Place sensor on BLACK line
wait_for_button_press()
black_value = read_average_light()

hub.light_matrix.write("F") # Place sensor on FLOOR
wait_for_button_press()
floor_value = read_average_light()

target = black_value
threshold_black = black_value + 10

hub.light_matrix.write("OK")
wait_for_seconds(0.5)
hub.light_matrix.off()

return target, threshold_black

# -----------------------------
# LINE FOLLOWING (PD CONTROL)
# -----------------------------
def follow_black_line_step(target, previous_error, speed):
light = color_sensor.get_reflected_light()
error = target - light
derivative = error - previous_error
steering = clamp(int(KP * error + KD * derivative))
drive.start(steering, speed)
return error

# -----------------------------
# WALL DETECTION
# -----------------------------
def detect_wall():
distance = distance_sensor.get_distance_cm()
return distance is not None and distance <= WALL_DISTANCE

# -----------------------------
# FIND BLACK LINE AFTER AVOIDING
# -----------------------------
def find_black_line(threshold_black, timeout=350):
for _ in range(timeout):
if color_sensor.get_reflected_light() <= threshold_black:
drive.stop()
return
drive.start(0, 15)
wait_for_seconds(0.02)
drive.stop()

# -----------------------------
# WALL AVOIDANCE ROUTINE
# -----------------------------
def avoid_wall(threshold_black):
drive.stop()
wait_for_seconds(0.1)

drive.start(100, 20)
wait_for_seconds(0.45)
drive.stop()

drive.start(0, 25)
wait_for_seconds(0.85)
drive.stop()

drive.start(-100, 20)
wait_for_seconds(0.45)
drive.stop()

find_black_line(threshold_black)

# -----------------------------
# MAIN MISSION LOOP
# -----------------------------
def mission(duration_seconds, target, threshold_black):
previous_error = 0
steps = int(duration_seconds / 0.02)

for _ in range(steps):
distance = distance_sensor.get_distance_cm()

if detect_wall():
avoid_wall(threshold_black)
previous_error = 0
else:
speed = BASE_SPEED
if distance is not None and distance <= SLOW_DISTANCE:
speed = SLOW_SPEED
previous_error = follow_black_line_step(target, previous_error, speed)

wait_for_seconds(0.02)

drive.stop()
hub.light_matrix.write("END")

# -----------------------------
# START PROGRAM
# -----------------------------
target, threshold_black = calibrate_black_line()
mission(20, target, threshold_black)
