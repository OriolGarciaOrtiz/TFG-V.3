from djitellopy import Tello


tello = Tello()
tello.connect()
print(tello.get_battery())

#tello.takeoff()

#tello.go_xyz_speed(0, 50, 0, 100)
#tello.send_control_command("flip l")
#tello.go_xyz_speed(50, 0, 0, 100)
#tello.go_xyz_speed(0, 0, 50, 100)
tello.send_control_command("EXT mled g 000000000rr00rr0rrrrrrrrrrrrrrrr0rrrrrr000rrrr00000rr00000000000")


#tello.land()

