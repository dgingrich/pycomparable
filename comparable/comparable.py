"""
DISCLAIMER:

Although this works (it really adds the rich comparison operators), it's for
fun/learning purposes only.  If you really need all the comparisons, you're
probably better off writing __cmp__.  I think Python3000 might automatically
create __ne__ based on __eq__.  The one real world use might be to easily
add all rich comparison methods to a subclass where the parent class
implements a subset of the operator.  But how often does that happen?  Just
use it for fun.


Try to add rich comparison methods (__eq__, __ne__, etc.) to an existing class.
It exports three names:

* comparable - class decorator
* ComparableMetaclass - Metaclass to automatically call comparable
* ComparableMixin - Mixin to automatically call comparable

comparable works as a class decorator.  It takes a class as an argument and
returns a decorated class.  comparable attempts to add the rich comparison
special methods if they are not defined.  If __eq__ is not defined, it will
try to define it as being not != or not (< or >), etc.  It then sets != as
the inversion of ==.  Finally it sets whatever inequalities are possible
(e.g. < === <= and not ==).

comparable will not overwrite existing methods.

comparable won't add methods if there is not enough information.  For
example, if only __eq__ and __ne__ are defined, it will not attempt to add
any inequalities.  It also won't raise any errors, so be warned.

ComparableMetaclass and ComparableMixin are additional ways to create a
comparable class.  Both are simply wrappers for the main comparable
function.

Inspired by this discussion turned rant on comp.lang.python
(http://groups.google.com/group/comp.lang.python/browse_thread/thread/a5fa8ff0ffadd6ee/1aa3b5d25eae91d5)
Loosely based on Ruby's comparable module
(http://www.ruby-doc.org/core/classes/Comparable.html) though I believe the
implementation is different.
"""


def comparable(cls):
    """Adds rich comparison special methods (__ne__, __gt__, etc.) to a
    passed in class and returns the modified class.  See ComparableMetaclass
    or ComparableMixin for other ways of running.
    """

    ops = dict((s, 'self.__%s__(o)' % s)
               for s in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'))
    def sub(s):
        for opk, opv in ops.items(): s = s.replace(opk, opv)
        return s
    mkfunc = lambda s: eval("lambda self, o: %s" % sub(s))
    has = lambda s: hasattr(cls, '__%s__' % s)
    set = lambda s, funcstr: \
          setattr(cls, '__%s__' % s, mkfunc(funcstr)) if not has(s) \
          else None

    # Set ==
    if not has('eq'):
        if has('ne'): set('eq', 'not ne')
        if has('gt') and has('lt'): set('eq', 'not (lt or gt)')
        if has('ge') and has('le'): set('eq', 'ge and le')
    if not has('eq'): return cls      # Abort if can't get equals
    # Set !=
    set('ne', 'not eq')
    # Set inequalities
    if has('lt'):
        set('le', 'lt or eq')
        set('gt', 'not le')
        set('ge', 'not lt')
    elif has('le'):
        set('lt', 'le and not eq')
        set('gt', 'not le')
        set('ge', 'not lt')
    elif has('gt'):
        set('ge', 'gt or eq')
        set('lt', 'not ge')
        set('le', 'not gt')
    elif has('ge'):
        set('gt', 'ge and not eq')
        set('lt', 'not ge')
        set('le', 'not gt')
    else:
        pass    # Silently succeed
    return cls


class ComparableMetaclass(type):
    """Metaclass that will automatically run comparable on your class"""
    def __new__(cls, *a, **ka):
        return comparable(super(ComparableMetaclass, cls).__new__(cls, *a, **ka))


class ComparableMixin(object):
    """Mixin to run comparable.  Simply uses the metaclass internally."""
    # Almost the same code as ComparableMetaclass, but ComparableMixin =
    # ComparableMetaclass fails, maybe because of super(...) call?
    def __new__(cls, *a, **ka):
        return comparable(super(ComparableMixin, cls).__new__(cls, *a, **ka))

