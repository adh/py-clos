import time
from example import *

start = time.time()
for i in range(10000):
    display(User(), Screen())
    display(User(), Webpage())
    get_path(User())
print(time.time() - start)

def foo():
    pass

start = time.time()
for i in range(100000):
    foo()
    foo()
    foo()
    
print(time.time() - start)
