# Importing threading and time module.
import threading,time

def main():
    # time.asctime() prints the current date & time in string.
    print('Program Executed @',time.asctime())

def run():
    # created a global variable.
    global counter
    counter += 1

    # stop after 5 executions
    if counter < 5:
        # where 5 is the number of seconds to wait
        threading.Timer(5, run).start()
    # running the main function
    main()

counter = 0
run()