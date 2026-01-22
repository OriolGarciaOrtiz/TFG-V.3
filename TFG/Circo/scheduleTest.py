import threading

derecha = "EXT mled g 000bb00000bb00000bb00000bbbbbbbbbbbbbbbb0bb0000000bb0000000bb000"
cont = 0
def fun():  # user defined function which adds +10 to given number
    global cont
    global derecha
    if cont == 0:
        print("derecha azul", derecha)
        cont  = cont +1
        start_time = threading.Timer(3, fun)
        start_time.start()
    elif cont == 1:
        derecha_roja = derecha.replace("b", "r")
        print("derecha roja", derecha_roja)







start_time = threading.Timer(3, fun)
start_time.start()
while True:
    pass

