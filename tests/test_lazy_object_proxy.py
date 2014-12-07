from __future__ import print_function

import imp
import sys
import pytest

from compat import PY2, PY3, exec_

PYPY = '__pypy__' in sys.builtin_module_names

OBJECTS_CODE = """
class TargetBaseClass(object):
    "documentation"

class Target(TargetBaseClass):
    "documentation"

def target():
    "documentation"
    pass
"""

objects = imp.new_module('objects')
exec_(OBJECTS_CODE, objects.__dict__, objects.__dict__)

@pytest.fixture(scope="module", params=["pure-python", "c-extension"])
def lazy_object_proxy(request):
    class mod:
        if request.param == "pure-python":
            from lazy_object_proxy.proxy import Proxy
        elif request.param == "c-extension":
            from lazy_object_proxy._proxy import Proxy
        else:
            raise RuntimeError("Unsupported param: %r." % request.param)
    return mod


def test_attributes(lazy_object_proxy):
    def function1(*args, **kwargs):
        return args, kwargs

    function2 = lazy_object_proxy.Proxy(function1)

    assert function2.__wrapped__ ==  function1


def test_get_wrapped(lazy_object_proxy):
    def function1(*args, **kwargs):
        return args, kwargs

    function2 = lazy_object_proxy.Proxy(function1)

    assert function2.__wrapped__ == function1

    function3 = lazy_object_proxy.Proxy(function2)

    assert function3.__wrapped__ == function1


def test_set_wrapped(lazy_object_proxy):
    def function1(*args, **kwargs):
        return args, kwargs

    function2 = lazy_object_proxy.Proxy(function1)

    assert function2 == function1
    assert function2.__wrapped__ == function1
    assert function2.__name__ == function1.__name__

    if PY3:
        assert function2.__qualname__ == function1.__qualname__

    function2.__wrapped__ = None

    assert not hasattr(function1, '__wrapped__')

    assert function2 == None
    assert function2.__wrapped__ == None
    assert not hasattr(function2, '__name__')

    if PY3:
        assert not hasattr(function2, '__qualname__')

    def function3(*args, **kwargs):
        return args, kwargs

    function2.__wrapped__ = function3

    assert function2 == function3
    assert function2.__wrapped__ == function3
    assert function2.__name__ == function3.__name__

    if PY3:
        assert function2.__qualname__ == function3.__qualname__


def test_delete_wrapped(lazy_object_proxy):
    def function1(*args, **kwargs):
        return args, kwargs

    function2 = lazy_object_proxy.Proxy(function1)

    def run(*args):
        del function2.__wrapped__

    pytest.raises(TypeError, run, ())


def test_proxy_attribute(lazy_object_proxy):
    def function1(*args, **kwargs):
        return args, kwargs

    function2 = lazy_object_proxy.Proxy(function1)

    function2._self_variable = True

    assert not hasattr(function1, '_self_variable')
    assert hasattr(function2, '_self_variable')

    assert function2._self_variable == True

    del function2._self_variable

    assert not hasattr(function1, '_self_variable')
    assert not hasattr(function2, '_self_variable')

    assert getattr(function2, '_self_variable', None) == None


def test_wrapped_attribute(lazy_object_proxy):
    def function1(*args, **kwargs):
        return args, kwargs

    function2 = lazy_object_proxy.Proxy(function1)

    function2.variable = True

    assert hasattr(function1, 'variable')
    assert hasattr(function2, 'variable')

    assert function2.variable == True

    del function2.variable

    assert not hasattr(function1, 'variable')
    assert not hasattr(function2, 'variable')

    assert getattr(function2, 'variable', None) == None


def test_class_object_name(lazy_object_proxy):
    # Test preservation of class __name__ attribute.

    target = objects.Target
    wrapper = lazy_object_proxy.Proxy(target)

    assert wrapper.__name__ == target.__name__


def test_class_object_qualname(lazy_object_proxy):
    # Test preservation of class __qualname__ attribute.

    target = objects.Target
    wrapper = lazy_object_proxy.Proxy(target)

    try:
        __qualname__ = target.__qualname__
    except AttributeError:
        pass
    else:
        assert wrapper.__qualname__ == __qualname__


def test_class_module_name(lazy_object_proxy):
    # Test preservation of class __module__ attribute.

    target = objects.Target
    wrapper = lazy_object_proxy.Proxy(target)

    assert wrapper.__module__ == target.__module__


def test_class_doc_string(lazy_object_proxy):
    # Test preservation of class __doc__ attribute.

    target = objects.Target
    wrapper = lazy_object_proxy.Proxy(target)

    assert wrapper.__doc__ == target.__doc__


def test_instance_module_name(lazy_object_proxy):
    # Test preservation of instance __module__ attribute.

    target = objects.Target()
    wrapper = lazy_object_proxy.Proxy(target)

    assert wrapper.__module__ == target.__module__


def test_instance_doc_string(lazy_object_proxy):
    # Test preservation of instance __doc__ attribute.

    target = objects.Target()
    wrapper = lazy_object_proxy.Proxy(target)

    assert wrapper.__doc__ == target.__doc__


def test_function_object_name(lazy_object_proxy):
    # Test preservation of function __name__ attribute.

    target = objects.target
    wrapper = lazy_object_proxy.Proxy(target)

    assert wrapper.__name__ == target.__name__


def test_function_object_qualname(lazy_object_proxy):
    # Test preservation of function __qualname__ attribute.

    target = objects.target
    wrapper = lazy_object_proxy.Proxy(target)

    try:
        __qualname__ = target.__qualname__
    except AttributeError:
        pass
    else:
        assert wrapper.__qualname__ == __qualname__


def test_function_module_name(lazy_object_proxy):
    # Test preservation of function __module__ attribute.

    target = objects.target
    wrapper = lazy_object_proxy.Proxy(target)

    assert wrapper.__module__ == target.__module__


def test_function_doc_string(lazy_object_proxy):
    # Test preservation of function __doc__ attribute.

    target = objects.target
    wrapper = lazy_object_proxy.Proxy(target)

    assert wrapper.__doc__ == target.__doc__


def test_class_of_class(lazy_object_proxy):
    # Test preservation of class __class__ attribute.

    target = objects.Target
    wrapper = lazy_object_proxy.Proxy(target)

    assert wrapper.__class__ == target.__class__

    assert isinstance(wrapper, type(target))


def test_class_of_instance(lazy_object_proxy):
    # Test preservation of instance __class__ attribute.

    target = objects.Target()
    wrapper = lazy_object_proxy.Proxy(target)

    assert wrapper.__class__ == target.__class__

    assert isinstance(wrapper, objects.Target)
    assert isinstance(wrapper, objects.TargetBaseClass)


def test_class_of_function(lazy_object_proxy):
    # Test preservation of function __class__ attribute.

    target = objects.target
    wrapper = lazy_object_proxy.Proxy(target)

    assert wrapper.__class__ == target.__class__

    assert isinstance(wrapper, type(target))


def test_dir_of_class(lazy_object_proxy):
    # Test preservation of class __dir__ attribute.

    target = objects.Target
    wrapper = lazy_object_proxy.Proxy(target)

    assert dir(wrapper) == dir(target)


def test_vars_of_class(lazy_object_proxy):
    # Test preservation of class __dir__ attribute.

    target = objects.Target
    wrapper = lazy_object_proxy.Proxy(target)

    assert vars(wrapper) == vars(target)


def test_dir_of_instance(lazy_object_proxy):
    # Test preservation of instance __dir__ attribute.

    target = objects.Target()
    wrapper = lazy_object_proxy.Proxy(target)

    assert dir(wrapper) == dir(target)


def test_vars_of_instance(lazy_object_proxy):
    # Test preservation of instance __dir__ attribute.

    target = objects.Target()
    wrapper = lazy_object_proxy.Proxy(target)

    assert vars(wrapper) == vars(target)


def test_dir_of_function(lazy_object_proxy):
    # Test preservation of function __dir__ attribute.

    target = objects.target
    wrapper = lazy_object_proxy.Proxy(target)

    assert dir(wrapper) == dir(target)


def test_vars_of_function(lazy_object_proxy):
    # Test preservation of function __dir__ attribute.

    target = objects.target
    wrapper = lazy_object_proxy.Proxy(target)

    assert vars(wrapper) == vars(target)


def test_function_no_args(lazy_object_proxy):
    _args = ()
    _kwargs = {}

    def function(*args, **kwargs):
        return args, kwargs

    wrapper = lazy_object_proxy.Proxy(function)

    result = wrapper()

    assert result, (_args == _kwargs)


def test_function_args(lazy_object_proxy):
    _args = (1, 2)
    _kwargs = {}

    def function(*args, **kwargs):
        return args, kwargs

    wrapper = lazy_object_proxy.Proxy(function)

    result = wrapper(*_args)

    assert result, (_args == _kwargs)


def test_function_kwargs(lazy_object_proxy):
    _args = ()
    _kwargs = {"one": 1, "two": 2}

    def function(*args, **kwargs):
        return args, kwargs

    wrapper = lazy_object_proxy.Proxy(function)

    result = wrapper(**_kwargs)

    assert result, (_args == _kwargs)


def test_function_args_plus_kwargs(lazy_object_proxy):
    _args = (1, 2)
    _kwargs = {"one": 1, "two": 2}

    def function(*args, **kwargs):
        return args, kwargs

    wrapper = lazy_object_proxy.Proxy(function)

    result = wrapper(*_args, **_kwargs)

    assert result, (_args == _kwargs)


def test_instancemethod_no_args(lazy_object_proxy):
    _args = ()
    _kwargs = {}

    class Class(object):
        def function(self, *args, **kwargs):
            return args, kwargs

    wrapper = lazy_object_proxy.Proxy(Class().function)

    result = wrapper()

    assert result, (_args == _kwargs)


def test_instancemethod_args(lazy_object_proxy):
    _args = (1, 2)
    _kwargs = {}

    class Class(object):
        def function(self, *args, **kwargs):
            return args, kwargs

    wrapper = lazy_object_proxy.Proxy(Class().function)

    result = wrapper(*_args)

    assert result, (_args == _kwargs)


def test_instancemethod_kwargs(lazy_object_proxy):
    _args = ()
    _kwargs = {"one": 1, "two": 2}

    class Class(object):
        def function(self, *args, **kwargs):
            return args, kwargs

    wrapper = lazy_object_proxy.Proxy(Class().function)

    result = wrapper(**_kwargs)

    assert result, (_args == _kwargs)


def test_instancemethod_args_plus_kwargs(lazy_object_proxy):
    _args = (1, 2)
    _kwargs = {"one": 1, "two": 2}

    class Class(object):
        def function(self, *args, **kwargs):
            return args, kwargs

    wrapper = lazy_object_proxy.Proxy(Class().function)

    result = wrapper(*_args, **_kwargs)

    assert result, (_args == _kwargs)


def test_instancemethod_via_class_no_args(lazy_object_proxy):
    _args = ()
    _kwargs = {}

    class Class(object):
        def function(self, *args, **kwargs):
            return args, kwargs

    wrapper = lazy_object_proxy.Proxy(Class.function)

    result = wrapper(Class())

    assert result, (_args == _kwargs)


def test_instancemethod_via_class_args(lazy_object_proxy):
    _args = (1, 2)
    _kwargs = {}

    class Class(object):
        def function(self, *args, **kwargs):
            return args, kwargs

    wrapper = lazy_object_proxy.Proxy(Class.function)

    result = wrapper(Class(), *_args)

    assert result, (_args == _kwargs)


def test_instancemethod_via_class_kwargs(lazy_object_proxy):
    _args = ()
    _kwargs = {"one": 1, "two": 2}

    class Class(object):
        def function(self, *args, **kwargs):
            return args, kwargs

    wrapper = lazy_object_proxy.Proxy(Class.function)

    result = wrapper(Class(), **_kwargs)

    assert result, (_args == _kwargs)


def test_instancemethod_via_class_args_plus_kwargs(lazy_object_proxy):
    _args = (1, 2)
    _kwargs = {"one": 1, "two": 2}

    class Class(object):
        def function(self, *args, **kwargs):
            return args, kwargs

    wrapper = lazy_object_proxy.Proxy(Class.function)

    result = wrapper(Class(), *_args, **_kwargs)

    assert result, (_args == _kwargs)


def test_classmethod_no_args(lazy_object_proxy):
    _args = ()
    _kwargs = {}

    class Class(object):
        @classmethod
        def function(cls, *args, **kwargs):
            return args, kwargs

    wrapper = lazy_object_proxy.Proxy(Class().function)

    result = wrapper()

    assert result, (_args == _kwargs)


def test_classmethod_args(lazy_object_proxy):
    _args = (1, 2)
    _kwargs = {}

    class Class(object):
        @classmethod
        def function(cls, *args, **kwargs):
            return args, kwargs

    wrapper = lazy_object_proxy.Proxy(Class().function)

    result = wrapper(*_args)

    assert result, (_args == _kwargs)


def test_classmethod_kwargs(lazy_object_proxy):
    _args = ()
    _kwargs = {"one": 1, "two": 2}

    class Class(object):
        @classmethod
        def function(cls, *args, **kwargs):
            return args, kwargs

    wrapper = lazy_object_proxy.Proxy(Class().function)

    result = wrapper(**_kwargs)

    assert result, (_args == _kwargs)


def test_classmethod_args_plus_kwargs(lazy_object_proxy):
    _args = (1, 2)
    _kwargs = {"one": 1, "two": 2}

    class Class(object):
        @classmethod
        def function(cls, *args, **kwargs):
            return args, kwargs

    wrapper = lazy_object_proxy.Proxy(Class().function)

    result = wrapper(*_args, **_kwargs)

    assert result, (_args == _kwargs)


def test_classmethod_via_class_no_args(lazy_object_proxy):
    _args = ()
    _kwargs = {}

    class Class(object):
        @classmethod
        def function(cls, *args, **kwargs):
            return args, kwargs

    wrapper = lazy_object_proxy.Proxy(Class.function)

    result = wrapper()

    assert result, (_args == _kwargs)


def test_classmethod_via_class_args(lazy_object_proxy):
    _args = (1, 2)
    _kwargs = {}

    class Class(object):
        @classmethod
        def function(cls, *args, **kwargs):
            return args, kwargs

    wrapper = lazy_object_proxy.Proxy(Class.function)

    result = wrapper(*_args)

    assert result, (_args == _kwargs)


def test_classmethod_via_class_kwargs(lazy_object_proxy):
    _args = ()
    _kwargs = {"one": 1, "two": 2}

    class Class(object):
        @classmethod
        def function(cls, *args, **kwargs):
            return args, kwargs

    wrapper = lazy_object_proxy.Proxy(Class.function)

    result = wrapper(**_kwargs)

    assert result, (_args == _kwargs)


def test_classmethod_via_class_args_plus_kwargs(lazy_object_proxy):
    _args = (1, 2)
    _kwargs = {"one": 1, "two": 2}

    class Class(object):
        @classmethod
        def function(cls, *args, **kwargs):
            return args, kwargs

    wrapper = lazy_object_proxy.Proxy(Class.function)

    result = wrapper(*_args, **_kwargs)

    assert result, (_args == _kwargs)


def test_staticmethod_no_args(lazy_object_proxy):
    _args = ()
    _kwargs = {}

    class Class(object):
        @staticmethod
        def function(*args, **kwargs):
            return args, kwargs

    wrapper = lazy_object_proxy.Proxy(Class().function)

    result = wrapper()

    assert result, (_args == _kwargs)


def test_staticmethod_args(lazy_object_proxy):
    _args = (1, 2)
    _kwargs = {}

    class Class(object):
        @staticmethod
        def function(*args, **kwargs):
            return args, kwargs

    wrapper = lazy_object_proxy.Proxy(Class().function)

    result = wrapper(*_args)

    assert result, (_args == _kwargs)


def test_staticmethod_kwargs(lazy_object_proxy):
    _args = ()
    _kwargs = {"one": 1, "two": 2}

    class Class(object):
        @staticmethod
        def function(*args, **kwargs):
            return args, kwargs

    wrapper = lazy_object_proxy.Proxy(Class().function)

    result = wrapper(**_kwargs)

    assert result, (_args == _kwargs)


def test_staticmethod_args_plus_kwargs(lazy_object_proxy):
    _args = (1, 2)
    _kwargs = {"one": 1, "two": 2}

    class Class(object):
        @staticmethod
        def function(*args, **kwargs):
            return args, kwargs

    wrapper = lazy_object_proxy.Proxy(Class().function)

    result = wrapper(*_args, **_kwargs)

    assert result, (_args == _kwargs)


def test_staticmethod_via_class_no_args(lazy_object_proxy):
    _args = ()
    _kwargs = {}

    class Class(object):
        @staticmethod
        def function(*args, **kwargs):
            return args, kwargs

    wrapper = lazy_object_proxy.Proxy(Class.function)

    result = wrapper()

    assert result, (_args == _kwargs)


def test_staticmethod_via_class_args(lazy_object_proxy):
    _args = (1, 2)
    _kwargs = {}

    class Class(object):
        @staticmethod
        def function(*args, **kwargs):
            return args, kwargs

    wrapper = lazy_object_proxy.Proxy(Class.function)

    result = wrapper(*_args)

    assert result, (_args == _kwargs)


def test_staticmethod_via_class_kwargs(lazy_object_proxy):
    _args = ()
    _kwargs = {"one": 1, "two": 2}

    class Class(object):
        @staticmethod
        def function(*args, **kwargs):
            return args, kwargs

    wrapper = lazy_object_proxy.Proxy(Class.function)

    result = wrapper(**_kwargs)

    assert result, (_args == _kwargs)


def test_staticmethod_via_class_args_plus_kwargs(lazy_object_proxy):
    _args = (1, 2)
    _kwargs = {"one": 1, "two": 2}

    class Class(object):
        @staticmethod
        def function(*args, **kwargs):
            return args, kwargs

    wrapper = lazy_object_proxy.Proxy(Class.function)

    result = wrapper(*_args, **_kwargs)

    assert result, (_args == _kwargs)


def test_iteration(lazy_object_proxy):
    items = [1, 2]

    wrapper = lazy_object_proxy.Proxy(items)

    result = [x for x in wrapper]

    assert result == items


def test_context_manager(lazy_object_proxy):
    class Class(object):
        def __enter__(self):
            return self

        def __exit__(*args, **kwargs):
            return

    instance = Class()

    wrapper = lazy_object_proxy.Proxy(instance)

    with wrapper:
        pass


def test_object_hash(lazy_object_proxy):
    def function1(*args, **kwargs):
        return args, kwargs

    function2 = lazy_object_proxy.Proxy(function1)

    assert hash(function2) == hash(function1)


def test_mapping_key(lazy_object_proxy):
    def function1(*args, **kwargs):
        return args, kwargs

    function2 = lazy_object_proxy.Proxy(function1)

    table = dict()
    table[function1] = True

    assert table.get(function2)

    table = dict()
    table[function2] = True

    assert table.get(function1)


def test_comparison(lazy_object_proxy):
    one = lazy_object_proxy.Proxy(1)
    two = lazy_object_proxy.Proxy(2)
    three = lazy_object_proxy.Proxy(3)

    assert two > 1
    assert two >= 1
    assert two < 3
    assert two <= 3
    assert two != 1
    assert two == 2
    assert two != 3

    assert 2 > one
    assert 2 >= one
    assert 2 < three
    assert 2 <= three
    assert 2 != one
    assert 2 == two
    assert 2 != three

    assert two > one
    assert two >= one
    assert two < three
    assert two <= three
    assert two != one
    assert two == two
    assert two != three


def test_nonzero(lazy_object_proxy):
    true = lazy_object_proxy.Proxy(True)
    false = lazy_object_proxy.Proxy(False)

    assert true
    assert not false

    assert bool(true)
    assert not bool(false)

    assert not false
    assert not not true


def test_int(lazy_object_proxy):
    one = lazy_object_proxy.Proxy(1)

    assert int(one) == 1

    if not PY3:
        assert long(one) == 1


def test_float(lazy_object_proxy):
    one = lazy_object_proxy.Proxy(1)

    assert float(one) == 1.0


def test_add(lazy_object_proxy):
    one = lazy_object_proxy.Proxy(1)
    two = lazy_object_proxy.Proxy(2)

    assert one + two == 1 + 2
    assert 1 + two == 1 + 2
    assert one + 2 == 1 + 2


def test_sub(lazy_object_proxy):
    one = lazy_object_proxy.Proxy(1)
    two = lazy_object_proxy.Proxy(2)

    assert one - two == 1 - 2
    assert 1 - two == 1 - 2
    assert one - 2 == 1 - 2


def test_mul(lazy_object_proxy):
    two = lazy_object_proxy.Proxy(2)
    three = lazy_object_proxy.Proxy(3)

    assert two * three == 2 * 3
    assert 2 * three == 2 * 3
    assert two * 3 == 2 * 3


def test_div(lazy_object_proxy):
    # On Python 2 this will pick up div and on Python
    # 3 it will pick up truediv.

    two = lazy_object_proxy.Proxy(2)
    three = lazy_object_proxy.Proxy(3)

    assert two / three == 2 / 3
    assert 2 / three == 2 / 3
    assert two / 3 == 2 / 3


def test_mod(lazy_object_proxy):
    two = lazy_object_proxy.Proxy(2)
    three = lazy_object_proxy.Proxy(3)

    assert three // two == 3 // 2
    assert 3 // two == 3 // 2
    assert three // 2 == 3 // 2


def test_mod(lazy_object_proxy):
    two = lazy_object_proxy.Proxy(2)
    three = lazy_object_proxy.Proxy(3)

    assert three % two == 3 % 2
    assert 3 % two == 3 % 2
    assert three % 2 == 3 % 2


def test_divmod(lazy_object_proxy):
    two = lazy_object_proxy.Proxy(2)
    three = lazy_object_proxy.Proxy(3)

    assert divmod(three, two), divmod(3 == 2)
    assert divmod(3, two), divmod(3 == 2)
    assert divmod(three, 2), divmod(3 == 2)


def test_pow(lazy_object_proxy):
    two = lazy_object_proxy.Proxy(2)
    three = lazy_object_proxy.Proxy(3)

    assert three ** two, pow(3 == 2)
    assert 3 ** two, pow(3 == 2)
    assert three ** 2, pow(3 == 2)

    assert pow(three, two), pow(3 == 2)
    assert pow(3, two), pow(3 == 2)
    assert pow(three, 2), pow(3 == 2)

    # Only PyPy implements __rpow__ for ternary pow().

    if PYPY:
        assert pow(three, two, 2), pow(3, 2 == 2)
        assert pow(3, two, 2), pow(3, 2 == 2)

    assert pow(three, 2, 2), pow(3, 2 == 2)


def test_lshift(lazy_object_proxy):
    two = lazy_object_proxy.Proxy(2)
    three = lazy_object_proxy.Proxy(3)

    assert three << two == 3 << 2
    assert 3 << two == 3 << 2
    assert three << 2 == 3 << 2


def test_rshift(lazy_object_proxy):
    two = lazy_object_proxy.Proxy(2)
    three = lazy_object_proxy.Proxy(3)

    assert three >> two == 3 >> 2
    assert 3 >> two == 3 >> 2
    assert three >> 2 == 3 >> 2


def test_and(lazy_object_proxy):
    two = lazy_object_proxy.Proxy(2)
    three = lazy_object_proxy.Proxy(3)

    assert three & two == 3 & 2
    assert 3 & two == 3 & 2
    assert three & 2 == 3 & 2


def test_xor(lazy_object_proxy):
    two = lazy_object_proxy.Proxy(2)
    three = lazy_object_proxy.Proxy(3)

    assert three ^ two == 3 ^ 2
    assert 3 ^ two == 3 ^ 2
    assert three ^ 2 == 3 ^ 2


def test_or(lazy_object_proxy):
    two = lazy_object_proxy.Proxy(2)
    three = lazy_object_proxy.Proxy(3)

    assert three | two == 3 | 2
    assert 3 | two == 3 | 2
    assert three | 2 == 3 | 2


def test_iadd(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(1)
    one = lazy_object_proxy.Proxy(1)

    value += 1
    assert value == 2

    assert type(value) == lazy_object_proxy.Proxy

    value += one
    assert value == 3

    assert type(value) == lazy_object_proxy.Proxy


def test_isub(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(1)
    one = lazy_object_proxy.Proxy(1)

    value -= 1
    assert value == 0

    assert type(value) == lazy_object_proxy.Proxy

    value -= one
    assert value == -1

    assert type(value) == lazy_object_proxy.Proxy


def test_imul(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(2)
    two = lazy_object_proxy.Proxy(2)

    value *= 2
    assert value == 4

    assert type(value) == lazy_object_proxy.Proxy

    value *= two
    assert value == 8

    assert type(value) == lazy_object_proxy.Proxy


def test_idiv(lazy_object_proxy):
    # On Python 2 this will pick up div and on Python
    # 3 it will pick up truediv.

    value = lazy_object_proxy.Proxy(2)
    two = lazy_object_proxy.Proxy(2)

    value /= 2
    assert value == 2 / 2

    assert type(value) == lazy_object_proxy.Proxy

    value /= two
    assert value == 2 / 2 / 2

    assert type(value) == lazy_object_proxy.Proxy


def test_ifloordiv(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(2)
    two = lazy_object_proxy.Proxy(2)

    value //= 2
    assert value == 2 // 2

    assert type(value) == lazy_object_proxy.Proxy

    value //= two
    assert value == 2 // 2 // 2

    assert type(value) == lazy_object_proxy.Proxy


def test_imod(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(10)
    two = lazy_object_proxy.Proxy(2)

    value %= 2
    assert value == 10 % 2

    assert type(value) == lazy_object_proxy.Proxy

    value %= two
    assert value == 10 % 2 % 2

    assert type(value) == lazy_object_proxy.Proxy


def test_ipow(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(10)
    two = lazy_object_proxy.Proxy(2)

    value **= 2
    assert value == 10 ** 2

    assert type(value) == lazy_object_proxy.Proxy

    value **= two
    assert value == 10 ** 2 ** 2

    assert type(value) == lazy_object_proxy.Proxy


def test_ilshift(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(256)
    two = lazy_object_proxy.Proxy(2)

    value <<= 2
    assert value == 256 << 2

    assert type(value) == lazy_object_proxy.Proxy

    value <<= two
    assert value == 256 << 2 << 2

    assert type(value) == lazy_object_proxy.Proxy


def test_irshift(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(2)
    two = lazy_object_proxy.Proxy(2)

    value >>= 2
    assert value == 2 >> 2

    assert type(value) == lazy_object_proxy.Proxy

    value >>= two
    assert value == 2 >> 2 >> 2

    assert type(value) == lazy_object_proxy.Proxy


def test_iand(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(1)
    two = lazy_object_proxy.Proxy(2)

    value &= 2
    assert value == 1 & 2

    assert type(value) == lazy_object_proxy.Proxy

    value &= two
    assert value == 1 & 2 & 2

    assert type(value) == lazy_object_proxy.Proxy


def test_ixor(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(1)
    two = lazy_object_proxy.Proxy(2)

    value ^= 2
    assert value == 1 ^ 2

    assert type(value) == lazy_object_proxy.Proxy

    value ^= two
    assert value == 1 ^ 2 ^ 2

    assert type(value) == lazy_object_proxy.Proxy


def test_ior(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(1)
    two = lazy_object_proxy.Proxy(2)

    value |= 2
    assert value == 1 | 2

    assert type(value) == lazy_object_proxy.Proxy

    value |= two
    assert value == 1 | 2 | 2

    assert type(value) == lazy_object_proxy.Proxy


def test_neg(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(1)

    assert -value == -1


def test_pos(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(1)

    assert +value == 1


def test_abs(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(-1)

    assert abs(value) == 1


def test_invert(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(1)

    assert ~value == ~1


def test_oct(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(20)

    assert oct(value) == oct(20)


def test_hex(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(20)

    assert hex(value) == hex(20)


def test_index(lazy_object_proxy):
    class Class(object):
        def __index__(self):
            return 1

    value = lazy_object_proxy.Proxy(Class())
    items = [0, 1, 2]

    assert items[value] == items[1]


def test_length(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(list(range(3)))

    assert len(value) == 3


def test_contains(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(list(range(3)))

    assert 2 in value
    assert not -2 in value


def test_getitem(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(list(range(3)))

    assert value[1] == 1


def test_setitem(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(list(range(3)))
    value[1] = -1

    assert value[1] == -1


def test_delitem(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(list(range(3)))

    assert len(value) == 3

    del value[1]

    assert len(value) == 2
    assert value[1] == 2


def test_getslice(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(list(range(5)))

    assert value[1:4], [1, 2 == 3]


def test_setslice(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(list(range(5)))

    value[1:4] = reversed(value[1:4])

    assert value[1:4], [3, 2 == 1]


def test_delslice(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(list(range(5)))

    del value[1:4]

    assert len(value) == 2
    assert value, [0 == 4]


def test_length(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(dict.fromkeys(range(3), False))

    assert len(value) == 3


def test_contains(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(dict.fromkeys(range(3), False))

    assert 2 in value
    assert not -2 in value


def test_getitem(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(dict.fromkeys(range(3), False))

    assert value[1] == False


def test_setitem(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(dict.fromkeys(range(3), False))
    value[1] = True

    assert value[1] == True


def test_delitem(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(dict.fromkeys(range(3), False))

    assert len(value) == 3

    del value[1]

    assert len(value) == 2


def test_str(lazy_object_proxy):
    value = lazy_object_proxy.Proxy(10)

    assert str(value) == str(10)

    value = lazy_object_proxy.Proxy((10,))

    assert str(value) == str((10,))

    value = lazy_object_proxy.Proxy([10])

    assert str(value) == str([10])

    value = lazy_object_proxy.Proxy({10: 10})

    assert str(value) == str({10: 10})


def test_repr(lazy_object_proxy):
    number = 10
    value = lazy_object_proxy.Proxy(number)

    self.assertNotEqual(repr(value).find('Proxy at'), -1)


def test_derived_new(lazy_object_proxy):
    class DerivedObjectProxy(lazy_object_proxy.Proxy):
        def __new__(cls, wrapped):
            instance = super(DerivedObjectProxy, cls).__new__(cls)
            instance.__init__(wrapped)

        def __init__(self, wrapped):
            super(DerivedObjectProxy, self).__init__(wrapped)

    def function():
        pass

    obj = DerivedObjectProxy(function)


def test_derived_setattr(lazy_object_proxy):
    class DerivedObjectProxy(lazy_object_proxy.Proxy):
        def __init__(self, wrapped):
            self._self_attribute = True
            super(DerivedObjectProxy, self).__init__(wrapped)

    def function():
        pass

    obj = DerivedObjectProxy(function)


def test_setup_class_attributes(lazy_object_proxy):
    def function():
        pass

    class DerivedObjectProxy(lazy_object_proxy.Proxy):
        pass

    obj = DerivedObjectProxy(function)

    DerivedObjectProxy.ATTRIBUTE = 1

    assert obj.ATTRIBUTE == 1
    assert not hasattr(function, 'ATTRIBUTE')

    del DerivedObjectProxy.ATTRIBUTE

    assert not hasattr(DerivedObjectProxy, 'ATTRIBUTE')
    assert not hasattr(obj, 'ATTRIBUTE')
    assert not hasattr(function, 'ATTRIBUTE')


def test_override_class_attributes(lazy_object_proxy):
    def function():
        pass

    class DerivedObjectProxy(lazy_object_proxy.Proxy):
        ATTRIBUTE = 1

    obj = DerivedObjectProxy(function)

    assert DerivedObjectProxy.ATTRIBUTE == 1
    assert obj.ATTRIBUTE == 1

    obj.ATTRIBUTE = 2

    assert DerivedObjectProxy.ATTRIBUTE == 1

    assert obj.ATTRIBUTE == 2
    assert not hasattr(function, 'ATTRIBUTE')

    del DerivedObjectProxy.ATTRIBUTE

    assert not hasattr(DerivedObjectProxy, 'ATTRIBUTE')
    assert obj.ATTRIBUTE == 2
    assert not hasattr(function, 'ATTRIBUTE')


def test_class_properties(lazy_object_proxy):
    def function():
        pass

    class DerivedObjectProxy(lazy_object_proxy.Proxy):
        def __init__(self, wrapped):
            super(DerivedObjectProxy, self).__init__(wrapped)
            self._self_attribute = 1

        @property
        def ATTRIBUTE(self):
            return self._self_attribute

        @ATTRIBUTE.setter
        def ATTRIBUTE(self, value):
            self._self_attribute = value

        @ATTRIBUTE.deleter
        def ATTRIBUTE(self):
            del self._self_attribute

    obj = DerivedObjectProxy(function)

    assert obj.ATTRIBUTE == 1

    obj.ATTRIBUTE = 2

    assert obj.ATTRIBUTE == 2
    assert not hasattr(function, 'ATTRIBUTE')

    del obj.ATTRIBUTE

    assert not hasattr(obj, 'ATTRIBUTE')
    assert not hasattr(function, 'ATTRIBUTE')

    obj.ATTRIBUTE = 1

    assert obj.ATTRIBUTE == 1

    obj.ATTRIBUTE = 2

    assert obj.ATTRIBUTE == 2
    assert not hasattr(function, 'ATTRIBUTE')

    del obj.ATTRIBUTE

    assert not hasattr(obj, 'ATTRIBUTE')
    assert not hasattr(function, 'ATTRIBUTE')


def test_attr_functions(lazy_object_proxy):
    def function():
        pass

    proxy = lazy_object_proxy.Proxy(function)

    assert hasattr(proxy, '__getattr__')
    assert hasattr(proxy, '__setattr__')
    assert hasattr(proxy, '__delattr__')


def test_override_getattr(lazy_object_proxy):
    def function():
        pass

    accessed = []

    class DerivedObjectProxy(lazy_object_proxy.Proxy):
        def __getattr__(self, name):
            accessed.append(name)
            try:
                __getattr__ = super(DerivedObjectProxy, self).__getattr__
            except AttributeError as e:
                raise RuntimeError(str(e))
            return __getattr__(name)

    function.attribute = 1

    proxy = DerivedObjectProxy(function)

    assert proxy.attribute == 1

    assert 'attribute' in accessed


def test_proxy_hasattr_call(lazy_object_proxy):
    proxy = lazy_object_proxy.Proxy(None)

    assert not hasattr(proxy, '__call__')


def test_proxy_getattr_call(lazy_object_proxy):
    proxy = lazy_object_proxy.Proxy(None)

    assert getattr(proxy, '__call__', None) == None


def test_proxy_is_callable(lazy_object_proxy):
    proxy = lazy_object_proxy.Proxy(None)

    assert not callable(proxy)


def test_callable_proxy_hasattr_call(lazy_object_proxy):
    proxy = lazy_object_proxy.Proxy(None)

    assert hasattr(proxy, '__call__')


def test_callable_proxy_getattr_call(lazy_object_proxy):
    proxy = lazy_object_proxy.Proxy(None)

    assert getattr(proxy, '__call__', None), None


def test_callable_proxy_is_callable(lazy_object_proxy):
    proxy = lazy_object_proxy.Proxy(None)

    assert callable(proxy)


def test_class_bytes(lazy_object_proxy):
    if PY3:
        class Class(object):
            def __bytes__(self):
                return b'BYTES'

        instance = Class()

        proxy = lazy_object_proxy.Proxy(instance)

        assert bytes(instance) == bytes(proxy)


def test_str_format(lazy_object_proxy):
    instance = 'abcd'

    proxy = lazy_object_proxy.Proxy(instance)

    assert format(instance, ''), format(proxy == '')


def test_list_reversed(lazy_object_proxy):
    instance = [1, 2]

    proxy = lazy_object_proxy.Proxy(instance)

    assert list(reversed(instance)) == list(reversed(proxy))


def test_decimal_complex(lazy_object_proxy):
    import decimal

    instance = decimal.Decimal(123)

    proxy = lazy_object_proxy.Proxy(instance)

    assert complex(instance) == complex(proxy)


def test_fractions_round(lazy_object_proxy):
    import fractions

    instance = fractions.Fraction('1/2')

    proxy = lazy_object_proxy.Proxy(instance)

    assert round(instance) == round(proxy)
