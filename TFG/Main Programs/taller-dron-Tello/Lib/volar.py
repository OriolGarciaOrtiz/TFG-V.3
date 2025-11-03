from djitellopy import Tello
import time

tello = Tello()
tello.connect()
print('BATERIA: ',tello.get_battery())

tello.takeoff()
#tello.move_left(20)
tello.move_up(20)
tello.rotate_clockwise(90)
tello.move_forward(20)
tello.land()