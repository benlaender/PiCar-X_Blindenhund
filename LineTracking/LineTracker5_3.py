from picarx import Picarx
from time import sleep
import readchar
import threading
from vilib import Vilib  # Ensure this is properly installed and configured
from robot_hat import TTS
import re

px = Picarx()
tts = TTS()
tts.lang("en-US")  # Set the language for TTS

px_power = 10
offset = 20
last_state = "stop"
running = True  # Controls the execution of the main loop and key listener
# Event to control the paused state
paused = threading.Event()
qr_code_flag = True  # Controls the execution of the QR code detection

#specific_qr_value = input("Enter the specific QR code value to stop the script: ")



#running = True  # Controls the main execution of the script --> already on line 16


def clean_qr_text(text):
    # Remove leading/trailing whitespace and make it case-insensitive.
    text = text.strip().lower()
    # Replace any sequence of whitespace characters with a single space
    text = re.sub(r'\s+', ' ', text)
    # Escape any other special characters if needed
    # text = re.escape(text)
    text = (text.replace('ü', 'ue')
                                           .replace('ä', 'ae')
                                           .replace('ö', 'oe')
                                           .replace('Ü', 'Ue')
                                           .replace('Ä', 'Ae')
                                           .replace('Ö', 'Oe')
                                           .replace('ß', 'ss'))  # Adding ß as well            
    print("Cleaned QR Text = " + text)    
    return text

#specific_qr_value = clean_qr_text(specific_qr_value)  # Clean the specific value right after input

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
    global running, paused, specific_qr_value

    while running:
        key = readchar.readkey()
        if key == 'p':
            if paused.is_set():
                paused.clear()  # Resume the car movement
                print("Script resumed.")
            else:
                paused.set()  # Pause the car movement
                px.stop()  # Physically stop the car
                print("Script paused.")
        elif key == 'q':
            running = False  # Stop the entire script
            paused.set()  # Make sure to break the pause loop in qrcode_detect
            px.stop()  # Physically stop the car
            print("Stopping script...")




def qrcode_detect():
    global running, paused, specific_qr_value
    Vilib.qrcode_detect_switch(True)
    print("QR code detection enabled. Waiting for QR code...")

    while running:
        # Thread should stop if running is set to False.
        if not running:
            break

        if paused.is_set():
            sleep(0.1)
            continue

        qr_data = Vilib.detect_obj_parameter['qr_data']
        if qr_data != "None":
            cleaned_text = clean_qr_text(qr_data)
            print('QR code: %s' % cleaned_text)
            tts.say(cleaned_text)

            if cleaned_text == specific_qr_value:
                px.stop()  # Physically stop the car
                print(f"Detected specific QR code '{specific_qr_value}'. Pausing.")
                Vilib.qrcode_detect_switch(False)  # Turn off QR detection
                paused.set()  # Set the paused flag

                while paused.is_set() and running:
                    # Check if the program is exiting
                    if not running:
                        break
                    sleep(0.1)

                if running:  # If still running, ask for the next QR code
                    Vilib.qrcode_detect_switch(True)  # Turn QR detection back on
                    specific_qr_value = input("Enter the next QR code value: ")
                    specific_qr_value = clean_qr_text(specific_qr_value)
                    print(f"Looking for QR code: '{specific_qr_value}'")
                else:
                    break  # Exit the loop if running is False

        sleep(0.5)

    Vilib.qrcode_detect_switch(False)
    print("QR code detection disabled.")



def run_line_following_and_qrcode_detection():
    global last_state, running, qr_code_flag
    key_thread = threading.Thread(target=key_listener)
    qr_thread = threading.Thread(target=qrcode_detect)  # Create a thread for QR code detection

    key_thread.start()
    qr_thread.start()  # Start the QR code detection thread

    try:
        # Main loop
        while running:
            # Check if the script is paused
            if paused.is_set():
                sleep(0.1)  # Sleep to prevent this loop from hogging CPU resources if paused
                continue  # Skip the rest of the loop if paused

            # If not paused, proceed with the line following logic
            gm_val_list = px.get_grayscale_data()
            gm_state = get_status(gm_val_list)

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
        # Cleanup actions
        px.stop()
        running = False
        qr_code_flag = False
        print("Stopped and exiting.")
        sleep(0.1)

        # Ensure threads are properly shut down
        key_thread.join()
        qr_thread.join()

def main():
    global specific_qr_value

    # Start the camera for QR code detection.
    Vilib.camera_start()
    print("Camera started for QR code detection.")

    # Get the initial QR code value to look for.
    specific_qr_value = input("Enter the specific QR code value to stop the script: ")
    specific_qr_value = clean_qr_text(specific_qr_value)

    # Initialize and start threads for key listening and QR code detection.
    key_listener_thread = threading.Thread(target=key_listener)
    qrcode_detect_thread = threading.Thread(target=qrcode_detect)
    
    key_listener_thread.start()
    qrcode_detect_thread.start()

    # Here, you can also include your line following logic or any other main script functionalities.
    run_line_following_and_qrcode_detection()

    # Wait for the threads to finish.
    key_listener_thread.join()
    qrcode_detect_thread.join()

    # Clean up before exiting.
    Vilib.camera_close()  # Ensure the camera is properly turned off.
    print("Camera stopped, and script exited cleanly.")

# Definitions for key_listener, qrcode_detect, run_line_following_and_qrcode_detection, and other necessary functions...

if __name__ == '__main__':
    main()
