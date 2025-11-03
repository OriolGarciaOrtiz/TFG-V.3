from djitellopy import Tello
import cv2
import time
##############################################
width = 320   # WIDTH OF THE IMAGE
height = 240  # HEIGHT OF THE IMAGE
startCounter = 0  # 0 FOR FLIGHT 1 FOR TESTING #Cambiarlo para probar
##############################################

# CONNECT TO TELLO
me = Tello()
me.connect()
me.for_back_velocity = 0
me.left_right_velocity = 0
me.up_down_velocity = 0
me.yaw_velocity = 0
me.speed = 0

print(me.get_battery())

me.streamoff()
me.streamon()

while True:
    # GET THE IMAGE FROM TELLO
    frame_read = me.get_frame_read() #Modulo de la libreria para coger el frame
    myFrame = frame_read.frame
    img = cv2.resize(myFrame, (width, height)) #Lo redimensionamos para que tenga los valores que tenemos y poder dividir la imagen en 9 zonas

    # TO GO UP IN THE BEGINNING
    if startCounter == 0:
        me.takeoff()
        time.sleep(8)
         #Nos movemos 20 cm a la izquierda y giramos en sentido horario 90 grados el dron para empezar
        me.rotate_clockwise(90)
        time.sleep(3)
        me.move_left(20)
        time.sleep(8)
        me.land()
        startCounter = 1

    # SEND VELOCITY VALUES TO TELLO
    # if me.send_rc_control:
    #     me.send_rc_control(me.left_right_velocity, me.for_back_velocity, me.up_down_velocity, me.yaw_velocity)

    # DISPLAY IMAGE
    cv2.imshow("MyResult", img)

    # WAIT FOR THE 'Q' BUTTON TO STOP
    if cv2.waitKey(1) & 0xFF == ord('q'): #Si le damos a la q paramos el dron
        me.land()
        break
