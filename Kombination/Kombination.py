from picarx import Picarx
from time import sleep
import time
import random
import threading
import readchar
from vilib import Vilib 
from robot_hat import TTS
import re

#NIEMALS DIE FORMATIERUNG ÄNDERN. Diese Variable stellen wichtige Parameter ein und sind immer so formatiert
Power = 30          #Gibt die Power der Motoren an
Straight = -2       #Wert für die Lenkung, um die Spurverstellung auszugleichen
Turning = 20        #Lenkwinkel
Safe = 50           #Sicherheitsdistanz
Danger = 25         #Distanz unter der stehen geblieben werden sollte
px=Picarx()         #Klammern nicht vergessen!!!
Move = 0.85         #So lange fährt das Picar während des Uturn vor und zurück

Right = Straight+Turning
Left = Straight-Turning

distance_left = 0
distance_right = 0
choose = Right
distance = 0

# Define flags for thread control
running = True  # Controls the execution of the main loop
qr_code_flag = True  # Controls the execution of the QR code detection
movement_allowed = True  # Allows controlling the movement separately

# --------------- Threading ------------ #
def key_listener():
    global running, movement_allowed, specific_qr_value 
    print("Press 'p' to pause/start the robot, 'q' to quit.")
    while running:
        key = readchar.readkey()
        if key == 'p':
            movement_allowed = not movement_allowed  # Toggle movement allowed
            if movement_allowed:
                print("Resuming operation...")
            else:
                print("Pausing operation...")
                px.stop()  # Make sure to stop the robot when pausing 
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
            movement_allowed = False
            print("Quitting program...")

# --------------- QR-Code -------------- #

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
    #print("Cleaned QR Text = " + text)    
    return text

def qrcode_detect():
    global qr_code_flag, running, movement_allowed, specific_qr_value
    detected_qr_codes = set()  # Track processed QR codes

    if qr_code_flag:
        Vilib.qrcode_detect_switch(True)
        print("Waiting for QR code")

    while running:
        temp = Vilib.detect_obj_parameter['qr_data']
        if temp and temp != "None":
            cleaned_text = clean_qr_text(temp)  # Clean the detected QR code text
            print('QR code detected: %s' % cleaned_text)
            if cleaned_text not in detected_qr_codes:  # Process new QR codes
                
                detected_qr_codes.add(cleaned_text)
                
                if cleaned_text == specific_qr_value:  # Compare cleaned texts
                    
                    tts.say(cleaned_text)
                    movement_allowed = False  # Temporarily stop movement for QR code change
                    
                    user_input = input(f"Specific QR code '{specific_qr_value}' found. Enter a new QR code value or press 'q' to quit: ")
                  

                    if user_input.lower() == 'q':
                        print("Quitting program...")
                        running = False  # Signal program to terminate
                        qr_code_flag = False  # Ensure QR code detection stops
                        
                        break  # Exit the loop immediately
                    else:
                        specific_qr_value = clean_qr_text(user_input)
                        print(f"QR code value updated to: {specific_qr_value}.")
                        
                    Vilib.qrcode_detect_switch(True)  # Resume QR code detection
                    movement_allowed = True
        sleep(0.1)
    px.forward(0)
    Vilib.qrcode_detect_switch(False)

def qrcode_detect():
    global qr_code_flag, running, movement_allowed, specific_qr_value
    detected_qr_codes = set()  # Track processed QR codes

    if qr_code_flag:
        Vilib.qrcode_detect_switch(True)
        print("Waiting for QR code")

    while running:
        temp = Vilib.detect_obj_parameter['qr_data']
        if temp and temp != "None":
            cleaned_text = clean_qr_text(temp)  # Clean the detected QR code text
            print('QR code detected: %s' % cleaned_text)
            if cleaned_text not in detected_qr_codes:  # Process new QR codes
                
                detected_qr_codes.add(cleaned_text)
                
                if cleaned_text == specific_qr_value:  # Compare cleaned texts
                    
                    tts.say(cleaned_text)
                    movement_allowed = False  # Temporarily stop movement for QR code change
                    
                    user_input = input(f"Specific QR code '{specific_qr_value}' found. Enter a new QR code value or press 'q' to quit: ")
                  

                    if user_input.lower() == 'q':
                        print("Quitting program...")
                        running = False  # Signal program to terminate
                        qr_code_flag = False  # Ensure QR code detection stops
                        
                        break  # Exit the loop immediately
                    else:
                        specific_qr_value = clean_qr_text(user_input)
                        print(f"QR code value updated to: {specific_qr_value}.")
                        
                    Vilib.qrcode_detect_switch(True)  # Resume QR code detection
                    movement_allowed = True
        sleep(0.1)
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
            print(f"QR code value changed to: {specific_qr_value} ")
            break  # Break the loop if the user confirms
        else:
            print("Change cancelled, no new QR code value set.")

# -------------- Ultrasonic-Driving -------------- #

def uturn():
    choose = Measuring() #Notwendig, da ansonsten choose wieder auf den Startwert zurückgesetzt wird
    #print(choose)
    for i in range(5): #Bestimmt wie oft er justiert 5 mal mit Distance = 0.85 => 180° Drehung
        if movement_allowed:
            uturn_move(choose)
    print("Uturn done.")

def uturn_move(Turn): #Justieren um sich neu auszurichten
    px.stop()
    px.set_dir_servo_angle(Straight)
    px.backward(Power)
    time.sleep(Move)
    px.stop() #Notwendig, damit das Auto stehen bleibt
    px.set_dir_servo_angle(Turn)
    time.sleep(0.1) #Zeit geben, um die Lenkung einzustellen
    px.forward(Power)
    time.sleep(Move)
    px.stop()
    px.set_dir_servo_angle(Straight)

def Measuring(): #Prüft den Abstand auf beiden Seiten
    px.stop()
    print("Entfernung messen...")
    px.set_dir_servo_angle(Left)
    px.forward(Power)
    time.sleep(0.4)
    distance_left= round(px.ultrasonic.read(), 2)
    px.stop()
    px.backward(Power)
    time.sleep(0.55)
    px.set_dir_servo_angle(Right)
    px.forward(Power)
    time.sleep(0.4)
    distance_right = round(px.ultrasonic.read(), 2)
    px.backward(Power)
    time.sleep(0.55)
    px.set_dir_servo_angle(Straight)
    px.stop()
    print("Links: ", distance_left, "cm, Rechts: ", distance_right, "cm")
    if distance_left > distance_right:
        choose = Left
    else:
        choose = Right
    #print(choose, " gemessen")
    return choose

def Bypass():
    distance = round(px.ultrasonic.read(), 2)
    px.set_dir_servo_angle(choose)

    while(distance <= Safe*1.2):
        if movement_allowed:
            if distance < 0.7*Danger:
                break
            px.forward(Power)
            time.sleep(0.5)
            px.set_dir_servo_angle(Straight)
            px.forward(Power)
            time.sleep(0.3)
            px.set_dir_servo_angle(choose)
            distance = round(px.ultrasonic.read(), 2)

    print("Driven around the obstacle")

# --------------- Movement ------------- #
def main():
    Vilib.camera_start()
    key_thread = threading.Thread(target=key_listener)
    qr_thread = threading.Thread(target=qrcode_detect)

    key_thread.start()
    qr_thread.start()

    try:
        #px = Picarx(ultrasonic_pins=['D2','D3']) # tring, echo
       
        safe_detect = 0
        danger_detect = 0
        while True:
            if movement_allowed:
                distance = round(px.ultrasonic.read(), 2)
                #print("distance: ",distance)
                if distance >= Safe:
                    px.set_dir_servo_angle(Straight)
                    px.forward(Power)
                elif distance >= Danger:
                    safe_detect +=1
                    print(f"safe_detect = {safe_detect}")
                    if safe_detect >= 3:
                        choose = Measuring()
                        #print (choose)
                        Bypass()
                        px.forward(0)
                        safe_detect = 0
                else:
                    danger_detect +=1
                    print(f"danger_detect = {danger_detect}")
                    if danger_detect >= 3:
                        uturn() #U-Turn statt einfachem Rückwärtsfahren
                        danger_detect = 0
            else:
                px.forward(0)

    finally:
        px.forward(0) #Hält die Räder am Ende an
        running = False
        qr_code_flag = False
        key_thread.join()
    Vilib.camera_close()

main()
