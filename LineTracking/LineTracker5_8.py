from picarx import Picarx
from time import sleep
import readchar
import threading
from vilib import Vilib  # Ensure this is properly installed and configured
from robot_hat import TTS
import re

px = Picarx()
tts = TTS()
tts.lang("de-DE")  # Set the language for TTS

px_power = 10  # Adjusted for demonstration; set your own speed
offset = 20

# Define flags for thread control
running = True  # Controls the execution of the main loop
qr_code_flag = True  # Controls the execution of the QR code detection
movement_allowed = True  # Allows controlling the movement separately


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
    global running, movement_allowed
    print("Press 'p' to pause/start the robot, 'q' to quit.")
    while running:
        key = readchar.readkey()
        if key == 'p':
            movement_allowed = not movement_allowed  # Toggle movement allowed
            if movement_allowed:
                print("Resuming operation...")
                Vilib.qrcode_detect_switch(True)
            else:
                print("Pausing operation...")
                px.stop()  # Make sure to stop the robot when pausing
                Vilib.qrcode_detect_switch(False)
        elif key == 'c':
           # Pause operation before changing QR code
            movement_allowed = False
            px.stop()
            
            print("Operation paused for QR code change.")
            
            # Change QR code value
            while True:
                new_qr_value = input("Enter the new QR code value (or 'cancel' to resume without changing): ")
                if new_qr_value.lower() == 'cancel':
                    print("QR code change cancelled. Resuming operation.")
                    break
                if new_qr_value.strip() == '':
                    print("Invalid input, please enter a valid QR code value.")
                    continue
                confirm = input(f"Change to this QR code '{new_qr_value}'? (yes/no): ")
                if confirm.lower() == 'yes':
                    specific_qr_value = clean_qr_text(new_qr_value)
                    print(f"QR code value changed to: {specific_qr_value}. Resuming operation.")
                    break
                else:
                    print("Change cancelled. Please enter the QR code value again or type 'cancel' to resume.")
            
            # Resume operation
            movement_allowed = True           
        elif key == 'q':
            running = False  # Set running to False to end all threads and stop the program
            print("Quitting program...")



def qrcode_detect():
    global qr_code_flag, running, movement_allowed, specific_qr_value
    if qr_code_flag:
        Vilib.qrcode_detect_switch(True)
        print("Waiting for QR code")

    while running:
        temp = Vilib.detect_obj_parameter['qr_data']
        if temp and temp != "None":
            cleaned_text = clean_qr_text(temp)  # Clean the detected QR code text
            print('QR code detected: %s' % cleaned_text)
            tts.say(cleaned_text)
            
            if cleaned_text == specific_qr_value:  # Compare cleaned texts
                movement_allowed = False  # Temporarily stop movement for QR code change
                user_input = input(f"Specific QR code '{specific_qr_value}' found. Enter a new QR code value or press 'q' to quit:")
                #user_input = input()
                if user_input.lower() == 'q':
                    print("Quitting program...")
                    running = False  # Signal program to terminate
                    qr_code_flag = False  # Ensure QR code detection stops
                    movement_allowed = True  # Reset flag to allow for any cleanup
                    break  # Exit the loop immediately
                else:
                    specific_qr_value = clean_qr_text(user_input)
                    print(f"QR code value updated to: {specific_qr_value}.")
                    
                    Vilib.qrcode_detect_switch(True)  # Resume QR code detection
                    movement_allowed = True
        sleep(0.5)
    Vilib.qrcode_detect_switch(False)

def change_qr_code():
    global specific_qr_value
    while True:
        user_input = input("Enter the new QR code value: ")
        if user_input.strip() == '':
            print("Invalid input, please enter a valid QR code value.")
            continue  # Prompt the user again if the input is invalid
        new_qr_value = clean_qr_text(user_input)
        # Confirm with the user
        confirm = input(f"Change to this QR code '{new_qr_value}'? (yes/no): ")
        if confirm.lower() == 'yes':
            specific_qr_value = new_qr_value
            print(f"QR code value changed to: {specific_qr_value}")
            break  # Break the loop if the user confirms
        else:
            print("Change cancelled, no new QR code value set.")

def line_following():
    global last_state, running, movement_allowed
    while running:
        if movement_allowed:
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
                px.stop()
        else:
            px.stop()
        sleep(0.1)

def run_line_following_and_qrcode_detection():
    global running, qr_code_flag, specific_qr_value
    specific_qr_value = input("Enter the specific QR code value to begin: ")
    specific_qr_value = clean_qr_text(specific_qr_value)

    key_thread = threading.Thread(target=key_listener)
    qr_thread = threading.Thread(target=qrcode_detect)
    line_thread = threading.Thread(target=line_following)

    key_thread.start()
    qr_thread.start()
    line_thread.start()

    try:
        while running:
            sleep(1)
    finally:
        running = False
        qr_code_flag = False
        px.stop()
        key_thread.join()
        qr_thread.join()
        line_thread.join()
        print("Stopped and exiting.")

if __name__ == '__main__':
    Vilib.camera_start()
    run_line_following_and_qrcode_detection()
    Vilib.camera_close()
