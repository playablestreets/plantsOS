## MAIN.pd 
- Runs on Pis. 
- Generates audio in response to incoming sensor data.

### Listening on 6660, 6661, 6662

### Broadcast 5550
    report to ADMIN.pd

### Unicast localhost:7770
    send to helper.py
    forward 6660:/helper/* to helper.py (localhost:7770)


### Unicast localhost:8880
    send to io/main.py
    forward 6660:/io/* to io/main.py (localhost:8880)


## ADMIN.pd
- Runs on laptop.
- Provides monitor and control of Pis.

### Listening on 5550

### Broadcast 6660
    Send to MAIN.pd

### Broadcast 7770
    Send to io/main.py

## helper.py
- Runs on Pis. 
- Issues OS and admin commands like shutdown and update.

### Listening 7770

### Unicast localhost:6661
    Send to MAIN.pd

## io/main.py 
- Runs on Pis. 
- Reads/writes to/from sensors and i2c peripherals.


### Listening 8880

### Unicast localhost:6662
    Send to MAIN.pd
