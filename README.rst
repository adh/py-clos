PyCLOS
======

PyCLOS implements CLOS-style generic functions for Python 3. Current
implementation is pure python with optional dependency on C
implemented lru-dict which gets used for dispatch caches in case of
specialization on value.

Example usage::

  from py_clos import generic
  @generic
  def display(what, where):
      return "{} on {}".format(what, where)

  @generic(qualifiers=["around"])
  def display(what, where: Webpage, next_method):
      return "<html>{}</html>".format(next_method(what, where))

  @generic
  def display(what: User, where):
      return "user"


