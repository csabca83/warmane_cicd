import sys


def asd (n):
    if n == 0:
        sys.exit()
    else:
        print(f"Points left {n}")
        asd(n-1)



asd(5)
    