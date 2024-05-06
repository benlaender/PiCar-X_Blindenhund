from picarx import Picarx
import time

Power = 30 #gibt die Power der Motoren an
Straight = -2 #Wert für die Lenkung, um die Spurverstellung auszugleichen
Safe = 70 #Sicherheitsdistanz
Danger = 30 #Distanz unter der stehen geblieben werden sollte
px=Picarx()
Distance = 0.85 #so lange fährt das Picar während des Uturn vor und zurück

def main():
    try:
        # px = Picarx(ultrasonic_pins=['D2','D3']) # tring, echo
       
        while True:
            distance = round(px.ultrasonic.read(), 2)
            #print("distance: ",distance)
            if distance >= Safe:
                px.set_dir_servo_angle(Straight)
                px.forward(Power)
            elif distance >= Danger:
                px.set_dir_servo_angle(Straight+20) #changed from 30 to 20 for higher maneuverability
                px.forward(Power)
                time.sleep(0.1)
            else:
                uturn()
                time.sleep(Distance)

    finally:
        px.forward(0)

def uturn():

    for i in range(5):
        uturn_move()
    print("Uturn done")

def uturn_move():
    px.stop
    px.set_dir_servo_angle(Straight)
    px.backward(Power)
    time.sleep(Distance)
    px.stop() #Notwendig, damit das Auto stehen bleibt
    px.set_dir_servo_angle(Straight-20)
    time.sleep(0.1) #Zeit geben, um die Lenkung einzustellen
    px.forward(Power)
    time.sleep(Distance)
    px.stop
    px.set_dir_servo_angle(Straight)


main()
