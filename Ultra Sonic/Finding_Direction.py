from picarx import Picarx
import time
import random

#NIEMALS DIE FORMATIERUNG ÄNDERN. Diese Variable stellen wichtige Parameter ein und sind immer so formatiert
Power = 30          #Gibt die Power der Motoren an
Straight = -2       #Wert für die Lenkung, um die Spurverstellung auszugleichen
Turning = 20        #Lenkwinkel
Safe = 50           #Sicherheitsdistanz
Danger = 25         #Distanz unter der stehen geblieben werden sollte
px=Picarx()         #Klammern nicht vergessen!!!
Move = 0.85     #So lange fährt das Picar während des Uturn vor und zurück

#Direction
Right = Straight+Turning
Left = Straight-Turning

distance_left = 0
distance_right = 0
choose = Left
distance = 0

def Measuring(): #Prüft den Abstand auf beiden Seiten
    px.stop()
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
    print("Entfernung \nLinks: ", distance_left, "cm, Rechts: ", distance_right, "cm")

def Bypass():
    if distance_left > distance_right:
        choose = Left
    else:
        choose = Right
    distance = round(px.ultrasonic.read(), 2)
    px.set_dir_servo_angle(choose)

    while(distance <= Safe):
        px.forward(Power)

    print("Driven around the obstacle")

    

Measuring()
Bypass()
px.forward(0)
