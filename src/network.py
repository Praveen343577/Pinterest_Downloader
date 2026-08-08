import socket
import time

def check_internet():
    endpoints = [
        ("8.8.8.8", 53),
        ("1.1.1.1", 53),
        ("www.google.com", 80)
    ]
    for host, port in endpoints:
        try:
            socket.setdefaulttimeout(3)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            s.close()
            return True
        except OSError:
            pass
    return False

def wait_for_internet(dash):
    if check_internet():
        return False
        
    delay = 1
    MAX_DELAY = 300
    
    while not check_internet():
        dash.set_pause(f"No Internet Connection! Retrying in {delay}s...")
        time.sleep(delay)
        delay = min(delay * 2, MAX_DELAY)
        
    dash.set_pause("Internet Restored! Resuming download...")
    time.sleep(2)
    return True
