import time

import tellopy
import random
import schedule

drone = tellopy.Tello()

print ('voy a conectar')
drone.connect()
drone.wait_for_connection(10.0)

drone.send_packet_data("EXT mled g 000000000rr00rr0rrrrrrrrrrrrrrrr0rrrrrr000rrrr00000rr00000000000")

'''print ('despego')
drone.takeoff()
drone.left(30)
time.sleep(3)
drone.left (0)

drone.send_packet_data("forward 40")
drone.send_packet_data("go 100 0 0 40")

drone.land()

print("Enviando comandos")

time.sleep(3)
'''

"""

El patron de la pantalla es una matriz de 8x8

para mandar un patron se mandan los 64 recuadros seguidos en orden de izquierda a derecha y de arriba hacia abajo:

Ejemplo: Si se quiere mandar solo la primera fila iluminada de rojo, el patron seria:

rrrrrrrr00000000000000000000000000000000000000000000000000000000

Si se quiere solo la ultima fila en lila seria:

00000000000000000000000000000000000000000000000000000000pppppppp

los colores posibles creo que son solo r(rojo), b(azul), p(lila)

"""
'''
atras = "EXT mled g 000000000000000000000000000bb000000bb000000000000000000000000000"
adelante = "EXT mled g 0000000000bbbb000bbbbbb00bbbbbb00bbbbbb00bbbbbb000bbbb0000000000"
arriba = "EXT mled g 000bb00000bbbb000bbbbbb0bb0bb0bbb00bb00b000bb000000bb000000bb000"
abajo = "EXT mled g 000bb000000bb000000bb000b00bb00bbb0bb0bb0bbbbbb000bbbb00000bb000"
izquierda = "EXT mled g 000bb00000bb00000bb00000bbbbbbbbbbbbbbbb0bb0000000bb0000000bb000"
izquierda_rojo = "EXT mled g 000rr00000rr00000rr00000rrrrrrrrrrrrrrrr0rr0000000rr0000000rr000"
derecha = "EXT mled g 000bb00000bb00000bb00000bbbbbbbbbbbbbbbb0bb0000000bb0000000bb000"
flip = "EXT mled g 00bbbb000b000000b00bbb00b00b00b00b00b0b000b000b0000bbb0000000000"
aterriza = "EXT mled g 0000000000000000000000000bbbbbb000000000000000000000000000000000"
corazon = "EXT mled g 000000000rr00rr0rrrrrrrrrrrrrrrr0rrrrrr000rrrr00000rr00000000000"
corazon_roto = "EXT mled g 000000000rr000r0rrrr0rrrrrrr0rrr0rrr0rr000r0rr00000rr00000000000"

color = 'azul'
def cambiar_color():
    global color
    if color == 'azul':
        drone.send_packet_data(izquierda_rojo)
        color = 'rojo'
    else:
        drone.send_packet_data(corazon_roto)
        return schedule.CancelJob



drone.send_packet_data(izquierda)
schedule.every(10).seconds.do (cambiar_color)
comandos = [atras, adelante, arriba, abajo, izquierda, derecha, flip]

ud=0
lr=0
fb=0

cont = 0
while cont < 10:
    n = random.randint(0,6)
    print ('ha salido ', n)
    if n == 0:
        if fb > -2:
            drone.send_packet_data(atras)
            cont = cont +1
            fb = fb-1
    if n == 1:
        if fb < 2:
            drone.send_packet_data(adelante)
            cont = cont +1
            fb = fb+1
    if n == 2:
        if ud < 3:
            drone.send_packet_data(arriba)
            cont = cont +1
            ud = ud +1

    if n == 3:
        if ud > -1:
            drone.send_packet_data(abajo)
            cont = cont +1
            ud = ud-1
    if n == 4:
        if lr > -3:
            drone.send_packet_data(izquierda)
            cont = cont + 1
            lr = lr - 1

    if n == 5:
        if lr < 3:
            drone.send_packet_data(derecha)
            cont = cont +1
            lr = lr + 1
    if n == 6:
        drone.send_packet_data(flip)
        cont = cont +1
    print ('posicion ', fb, ud,lr)
    time.sleep(3)


drone.send_packet_data(aterriza)
time.sleep(3)

drone.send_packet_data(atras)
time.sleep(3)
drone.send_packet_data(adelante)
time.sleep(3)
drone.send_packet_data(arriba)
time.sleep(3)
drone.send_packet_data(abajo)
time.sleep(3)
drone.send_packet_data(izquierda)
time.sleep(3)
drone.send_packet_data(derecha)
time.sleep(3)
drone.send_packet_data(aterriza)
time.sleep(3)
drone.send_packet_data(flip)
time.sleep(3)
'''
"""

# Corazon

drone.send_packet_data("EXT mled g 000000000rr00rr0rrrrrrrrrrrrrrrr0rrrrrr000rrrr00000rr00000000000")

time.sleep(3)

# Sonrisa

drone.send_packet_data("EXT mled g 00pppp000p0000p0p0p00p0pp000000pp0p00p0pp00pp00p0p0000p000pppp00")

time.sleep(3)

# Cara triste

drone.send_packet_data("EXT mled g 00pppp000p0000p0p0p00p0pp000000pp00pp00pp0p00p0p0p0000p000pppp00")

time.sleep(3)

# Escribir texto

drone.send_packet_data("EXT mled l r 2.5 HOLA")

time.sleep(6)

# Pantalla moviendose con un patron (hacia arriba)

drone.send_packet_data("EXT mled u g 2.5 0000b00bbb0b0b000b00b00000bb0000000b0000bbb00bbb000b0b0b0b00b0b0")

time.sleep(3)



Otros comandos para mandar en "send_packet_data":

EXT mled s p I   # write a letter

EXT mled sg 0000000000000000000000000000000000000000000000000000000000000000    # make a starting pattern

EXT led 255 255 255  # turn on top led

"""