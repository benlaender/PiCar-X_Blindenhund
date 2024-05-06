from picarx import Picarx
import time

Power = 30 #gibt die Power der Motoren an
Straight = -2 #Wert für die Lenkung, um die Spurverstellung auszugleichen
Safe = 70 #Sicherheitsdistanz
Danger = 30 #Distanz unter der stehen geblieben werden sollte
px=Picarx()
Move = 0.85 #so lange fährt das Picar während des Uturn vor und zurück

def uturn():

    for i in range(5):
        uturn_move()
    print("Uturn done")

def uturn_move():
    px.stop
    px.set_dir_servo_angle(Straight)
    px.backward(Power)
    time.sleep(Move)
    px.stop() #Notwendig, damit das Auto stehen bleibt
    px.set_dir_servo_angle(Straight-20)
    time.sleep(0.1) #Zeit geben, um die Lenkung einzustellen
    px.forward(Power)
    time.sleep(Move)
    px.stop
    px.set_dir_servo_angle(Straight)


uturn()
px.forward(0)
