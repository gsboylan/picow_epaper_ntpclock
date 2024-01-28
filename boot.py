print("boot.py running...")


from machine import Pin


safe_mode_pin = Pin(0, Pin.IN, Pin.PULL_UP)
if not safe_mode_pin.value():
    print("booting in real mode")
    import program
    program.run()
else:
    print("\n\n\n SAFE MODE \n\n\n")
