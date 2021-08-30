from datetime import datetime


# Simple logging method
def log(s, t=None):
    now = datetime.now()
    if t is None:
        t = "Main"
    print("%s :: %s -> %s " % (str(now), t, s))
