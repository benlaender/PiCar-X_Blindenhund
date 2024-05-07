
from picarx import Picarx
from time import sleep
import readchar
import threading

# Initialization
px = Picarx()
px_power = 10
offset = 20
last_state = "stop"
running = True  # A flag to control the running of the main loop

def outHandle():
    global last_state, current_state
    if last_state == 'left':
        px.set_dir_servo_angle(-30)
        px.backward(10)
    elif last_state == 'right':
        px.set_dir_servo_angle(30)
        px.backward(10)
    while True:
        gm_val_list = px.get_grayscale_data()
        gm_state = get_status(gm_val_list)
        print("outHandle gm_val_list: %s, %s"%(gm_val_list, gm_state))
        currentSta = gm_state
        if currentSta != last_state:
            break
    sleep(0.001)

def get_status(val_list):
    _state = px.get_line_status(val_list)  # [bool, bool, bool], 0 means line, 1 means background
    if _state == [0, 0, 0]:
        return 'stop'
    elif _state[1] == 1:
        return 'forward'
    elif _state[0] == 1:
        return 'right'
    elif _state[2] == 1:
        return 'left'

def key_listener():
    global running
    while running:
        key = readchar.readkey()
        if key == 'q':
            running = False
            print("Quitting program...")

def run_line_following():
    global last_state, running
    key_thread = threading.Thread(target=key_listener)  # Create a thread for listening to key presses
    key_thread.start()  # Start the thread

    try:
        while running:
            gm_val_list = px.get_grayscale_data()
            gm_state = get_status(gm_val_list)
            print("gm_val_list: %s, %s" % (gm_val_list, gm_state))

            if gm_state != "stop":
                last_state = gm_state

            if gm_state == 'forward':
                px.set_dir_servo_angle(0)
                px.forward(px_power)
            elif gm_state == 'left':
                px.set_dir_servo_angle(offset)
                px.forward(px_power)
            elif gm_state == 'right':
                px.set_dir_servo_angle(-offset)
                px.forward(px_power)
            else:
                outHandle()
    finally:
        px.stop()
        print("Stopped and exiting.")
        sleep(0.1)
        running = False
        key_thread.join()  # Wait for the key listener thread to finish

if __name__ == '__main__':
    run_line_following()
