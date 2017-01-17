import time
from example import *

start = time.time()
for i in range(100000):
    display(User(), Screen())
    display(User(), Webpage())
print(time.time() - start)

class A:
    def foo(self):
        return 'a'
class B(A):
    pass

a = A()
b = B()

start = time.time()
for i in range(100000):
    a.foo()
    b.foo()
    
print(time.time() - start)
