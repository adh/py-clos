from py_clos import generic

class Screen:
    pass

class Printer:
    pass

class Webpage(Screen):
    pass

class Entity:
    pass
    
class Person(Entity):
    pass
    
class User(Person):
    pass

@generic
def display(what, where):
    return "{} on {}".format(what, where)

@generic(qualifiers=["around"])
def display(what, where: Webpage, next_method):
    return "<html>{}</html>".format(next_method(what, where))

@generic
def display(what: User, where):
    return "user"

print(display(User(), Screen()))
print(display(User(), Webpage()))
    
