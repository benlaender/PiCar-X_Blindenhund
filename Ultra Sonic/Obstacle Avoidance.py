from picarx import Picarx
import time

POWER = 30 #changed from 50 to 30 to decrease speed
SafeDistance = 40   # > 40 safe
DangerDistance = 20 # > 20 && < 40 turn around, 
                    # < 20 backward

def main():
    try:
        px = Picarx()
        # px = Picarx(ultrasonic_pins=['D2','D3']) # tring, echo
       
        while True:
            distance = round(px.ultrasonic.read(), 2)
            print("distance: ",distance)
            if distance >= SafeDistance:
                px.set_dir_servo_angle(-2)
                px.forward(POWER)
            elif distance >= DangerDistance:
                px.set_dir_servo_angle(18) #changed from 30 to 20 for higher maneuverability
                px.forward(POWER)
                time.sleep(0.1)
            else:
                px.set_dir_servo_angle(-22) #changed from 30 to 20 for higher maneuverability
                px.backward(POWER)
                time.sleep(0.5)

    finally:
        px.forward(0)


if __name__ == "__main__":
    main()

