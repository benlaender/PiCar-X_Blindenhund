from picarx import Picarx
import time
import random
import threading
import readchar

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



running = True
movement_allowed = True

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
        elif key == 'q':
            running = False  # Set running to False to end all threads and stop the program
            print("Quitting program...")

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

def main():
    key_thread = threading.Thread(target=key_listener)

    key_thread.start()

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
                    if safe_detect >= 3:
                        choose = Measuring()
                        #print (choose)
                        Bypass()
                        px.forward(0)
                        safe_detect = 0
                else:
                    danger_detect +=1
                    if danger_detect >= 3:
                        uturn() #U-Turn statt einfachem Rückwärtsfahren
                        danger_detect = 0
            else:
                px.forward(0)

    finally:
        px.forward(0) #Hält die Räder am Ende an

main()
