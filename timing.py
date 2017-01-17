import time
from py_clos import generic

class A:
    def foo(self):
        return 'a'
class B(A):
    pass

class C(B):
    def foo(self):
        return 'c'

a = A()
b = B()
c = C()

@generic
def foo(a: A):
    return 'a'

@generic
def foo(c: C):
    return 'c'

start = time.time()
for i in range(100000):
    foo(a)
    foo(b)
    foo(c)

print(time.time() - start)


start = time.time()
for i in range(100000):
    a.foo()
    b.foo()
    c.foo()
    
print(time.time() - start)
