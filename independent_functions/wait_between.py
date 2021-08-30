from random import uniform
from time import sleep


# Use sleep for waiting and uniform for randomizing
def wait_between(a, b):
    rand = uniform(a, b)
    sleep(rand)
