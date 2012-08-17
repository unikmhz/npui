from .errors import PhpUnserializationError, PhpSerializationError, \
    _PhpUnserializationError


cdef extern from "Python.h":
    ctypedef void PyObject
    ctypedef struct PyTypeObject
    int PyObject_TypeCheck(object, PyTypeObject*)


cdef inline bint typecheck(object ob, object tp):
    return PyObject_TypeCheck(ob, <PyTypeObject*>tp)


class PHP_Class(object):
    def __init__(self, name, properties=()):
        self.name = name
        self._properties = {}
        for prop in properties:
            self._properties[prop.name] = prop

    def set_item(self, php_name, value=None):
        prop = PHP_Property(php_name, value)
        self._properties[prop.name] = prop

    def __iter__(self):
        return iter(self._properties.values())

    def __len__(self):
        return len(self._properties)

    def __repr__(self):
        return "PHP_Class(%s, %s)" % (repr(self.name), list(self))

    __str__ = __repr__

    def __getitem__(self, name):
        return self._properties[name].value

    def __eq__(self, other):
        return repr(self) == repr(other)


class PHP_Property(object):
    SEPARATOR = '\x00'
    def __init__(self, php_name, value):
        self.php_name = php_name
        self.name = php_name.split(self.SEPARATOR)[-1]
        self.value = value

    def __repr__(self):
        return 'PHP_Property(%s, %s)' % (repr(self.php_name), repr(self.value))

    __str__ = __repr__


def unserialize(s):
    """
    Unserialize python struct from php serialization format
    """
    try:
        return Unserializator(s).unserialize()
    except _PhpUnserializationError as e:
        char = len(str(s)) - len(e.rest)
        delta = 50
        try:
            message = '%s in %s' % (e.message,
                '...%s --> %s <-- %s...' % (s[(char > delta and char - delta or 0):char], s[char], s[char + 1:char + delta]))
        except Exception as e:
            print e
            raise
        print message
        raise PhpUnserializationError(message)

def serialize(struct):
    return do_serialize(struct)
    
cdef str do_serialize(object struct):
    """
    Serialize python struct into php serialization format
    """
    # N;
    if struct is None:
        return 'N;'

    struct_type = type(struct)
    # d:<float>;
    if struct_type is float:
        return 'd:%.20f;' % struct  # 20 digits after comma

    # b:<0 or 1>;
    if struct_type is bool:
        return 'b:%d;' % int(struct)

    # i:<integer>;
    if struct_type is int or struct_type is int:
        return 'i:%d;' % struct

    # s:<string_length>:"<string>";
    if struct_type is str:
        return 's:%d:"%s";' % (len(struct), struct)

    if struct_type is str:
        return do_serialize(struct.encode('utf-8'))

    if struct_type is dict:
         # a:<hash_length>:{<key><value><key2><value2>...<keyN><valueN>}
        core = ''.join([do_serialize(k) + do_serialize(struct[k]) for k in struct])
        return 'a:%d:{%s}' % (len(struct), core)  
        
    if struct_type is tuple or struct_type is list:
        return do_serialize(dict(enumerate(struct)))

    if isinstance(struct, PHP_Class):
        return 'O:%d:"%s":%d:{%s}' % (
            len(struct.name),
            struct.name,
            len(struct),
            ''.join([do_serialize(x.php_name) + do_serialize(x.value) for x in struct]),
        )
        
    raise PhpSerializationError('PHP serialize: cannot encode `%s`' % struct)


cdef class Unserializator(object):
    cdef int _position
    cdef str _str
    
    def __init__(self, s):
        self._position = 0
        self._str = s

    cdef inline void await(self, symbol, n=1):
        result = self.take(n)
        if result != symbol:
            raise _PhpUnserializationError('Next is `%s` not `%s`' % (result, symbol), self.get_rest())

    cdef inline str take(self, n=1):
        result = self._str[self._position:self._position + n]
        self._position += n
        return result

    cdef str take_while_not(self, str stopsymbol):
        try:
            stopsymbol_position = self._str.index(stopsymbol, self._position)
        except ValueError:
            raise _PhpUnserializationError('No `%s`' % stopsymbol, self.get_rest())
        result = self._str[self._position:stopsymbol_position]
        self._position = stopsymbol_position + 1
        return result

    cdef str get_rest(self):
        return self._str[self._position:]

    cdef dict parse_hash_core(self, size):
        result = {}
        self.await('{')
        for i from 0 <= i < size:
            k = self.unserialize()
            v = self.unserialize()
            result[k] = v
        self.await('}')
        return result

    def unserialize(self):
        t = self.take()

        if t == 'N':
            self.await(';')
            return None

        self.await(':')

        if t == 'i':
            return int(self.take_while_not(';'))
            
        if t == 'd':
            return float(self.take_while_not(';'))

        if t == 'b':
            return bool(int(self.take_while_not(';')))

        if t == 's':
            size = int(self.take_while_not(':'))
            self.await('"')
            result = self.take(size)
            self.await('"')
            self.await(';')
            return result

        if t == 'a':
            size = int(self.take_while_not(':'))
            result = self.parse_hash_core(size)
            if result.keys() == range(size):
                return result.values()
            else:
                return result            

        if t == 'O':
            object_name_size = int(self.take_while_not(':'))
            self.await('"')
            object_name = self.take(object_name_size)
            self.await('"')
            self.await(':')
            object_length = int(self.take_while_not(':'))            
            php_class = PHP_Class(object_name)
            members = self.parse_hash_core(object_length)
            if members:
                for php_name, value in members.items():
                    php_class.set_item(php_name, value)
            return php_class

        raise _PhpUnserializationError('Unknown type `%s`' % t, self.get_rest())
