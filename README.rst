PyCLOS
======

PyCLOS implements CLOS-style generic functions for
Python 3. Implementation depends on CPython and uses C extension
module for reasonable performance, but the core functionality is
written in pure Python. User code can define both custom specializers
and custom method combinations.

Example usage::

  from py_clos import generic
  @generic
  def display(what, where):
      return "{} on {}".format(what, where)

  @generic.around
  def display(what, where: Webpage, next_method):
      return "<html>{}</html>".format(next_method(what, where))

  @generic
  def display(what: User, where):
      return "user"


