from picarx import Picarx
from time import sleep
import readchar
import threading
from vilib import Vilib  # Ensure this is properly installed and configured
from robot_hat import TTS


px = Picarx()
tts = TTS()
tts.lang("en-US")  # Set the language for TTS

px_power = 10
offset = 20
last_state = "stop"
running = True  # Controls the execution of the main loop and key listener
qr_code_flag = True  # Controls the execution of the QR code detection

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
        #print("outHandle gm_val_list: %s, %s"%(gm_val_list, gm_state))
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

def qrcode_detect():
    global qr_code_flag
    if qr_code_flag:
        Vilib.qrcode_detect_switch(True)
        print("Waiting for QR code")

    text = None
    while running:  # Use the global running flag to control this loop as well
        temp = Vilib.detect_obj_parameter['qr_data']
        if temp != "None" and temp != text:
            text = temp
            cleaned_text = text.replace('"', '\\').replace("\n", " ")
            print("QR code: " + cleaned_text)
            tts.say(cleaned_text)
        sleep(0.5)
    Vilib.qrcode_detect_switch(False)

def run_line_following():
    global last_state, running, qr_code_flag
    key_thread = threading.Thread(target=key_listener)
    qr_thread = threading.Thread(target=qrcode_detect)  # Create a thread for QR code detection

    key_thread.start()
    qr_thread.start()  # Start the QR code detection thread

    try:
        while running:
            gm_val_list = px.get_grayscale_data()
            gm_state = get_status(gm_val_list)
            #print("gm_val_list: %s, %s" % (gm_val_list, gm_state))

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
        running = False
        qr_code_flag = False
        print("Stopped and exiting.")
        sleep(0.1)
        key_thread.join()
        qr_thread.join()  # Ensure the QR code detection thread is also joined

if __name__ == '__main__':
    Vilib.camera_start()  # Ensure the camera is started for QR code detection
    run_line_following()
    Vilib.camera_close()  # Cleanup by stopping the camera
