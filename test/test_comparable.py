#!/usr/bin/env python
import sys; sys.path.append('..')
import nose
from pycomparable import *


## Basic use (class decorator)

def attach(cls, fn, val):
    """Attach rich comparison function to the class"""
    setattr(cls, '__%s__' % fn, lambda self, o: val)


def mkclass(**rcfns):
    """Make an empty class and then attach rich comparison operators"""
    cls = type('testClass', (object,), {})
    for k, v in rcfns.items():
        attach(cls, k, v)
    return cls


def test_ne_eq():
    assert mkclass(eq=False)() != 'whatever'
    assert comparable(mkclass(eq=False))() != 'whatever'
    assert comparable(mkclass(eq=False))().__ne__('test')
    assert mkclass(ne=True)() != 'anything'
    assert comparable(mkclass(ne=True))() != 'anything'
    assert not comparable(mkclass(ne=True))().__eq__('anything')


def test_eq_from_gt_lt():
    assert comparable(mkclass(gt=False, lt=False))().__eq__('x')
    assert not comparable(mkclass(gt=True, lt=False))().__eq__('x')


def test_eq_from_ge_le():
    assert comparable(mkclass(ge=True, le=True))().__eq__('x')
    assert not comparable(mkclass(ge=False, le=True))().__eq__('x')
    assert not comparable(mkclass(ge=True, le=False))().__eq__('x')


def test_ineq_lt():
    obj = comparable(mkclass(eq="False", lt="True"))()
    assert obj.__le__('x')
    assert not obj.__gt__('x') 
    assert not obj.__ge__('x')


def test_ineq_le():
    obj = comparable(mkclass(eq="True", le="True"))()
    assert not obj.__lt__('x')
    assert not obj.__gt__('x') 
    assert obj.__ge__('x')


def test_ineq_gt():
    obj = comparable(mkclass(eq="False", gt="True"))()
    assert obj.__ge__('x')
    assert not obj.__lt__('x') 
    assert not obj.__le__('x')


def test_ineq_ge():
    obj = comparable(mkclass(eq="True", ge="True"))()
    assert not obj.__gt__('x')
    assert not obj.__lt__('x') 
    assert obj.__le__('x')



## Metaclass & mix-in

def assert_has_rcomps(obj):
    """Helper to check for existence of all rich comparison methods"""
    for rcomp in ['eq', 'ne', 'gt', 'ge', 'lt', 'le']:
        assert hasattr(obj, '__%s__' % rcomp)


def test_metaclass():
    class TestCls(object):
        __metaclass__ = ComparableMetaclass
        __eq__ = lambda self, o: True
        __lt__ = lambda self, o: False
    assert_has_rcomps(TestCls())


def test_mixin():
    class TestCls(ComparableMixin):
        __eq__ = lambda self, o: True
        __lt__ = lambda self, o: False
    assert_has_rcomps(TestCls())


def test_mixin_mi():
    """Does comparable mixin works w/ MI (other __new__'s get called)"""
    class TestMixin(object):
        def __new__(cls, *a, **ka):
            newcls = super(TestMixin, cls).__new__(cls, *a, **ka)
            newcls.foo = 'bar'
            return newcls
    class TestClass(TestMixin, ComparableMixin):
        __eq__ = lambda self, o: True
        __lt__ = lambda self, o: False
    obj = TestClass()
    assert_has_rcomps(obj)
    assert obj.foo == 'bar'


def test_mixin_mi_metaclass():
    """Does comparable mixin work in MI where other class uses metaclass"""
    class TestMetaClass(type):
        def __new__(cls, *a, **ka):
            newcls = super(TestMetaClass, cls).__new__(cls, *a, **ka)
            newcls.foo = 'bar'
            return newcls
    class TestMixin(object):
        __metaclass__ = TestMetaClass
    class TestClass(TestMixin, ComparableMixin):
        __eq__ = lambda self, o: True
        __lt__ = lambda self, o: False
    obj = TestClass()
    assert_has_rcomps(obj)
    assert obj.foo == 'bar'


## Misc

def test_docstring():
    """Docstring should be large, should be imported from comparable"""
    import pycomparable
    assert len(pycomparable.__doc__) > 100      # 100 is arbitrary


if __name__ == '__main__':
    nose.runmodule()
