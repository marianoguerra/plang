Hagamos un lenguaje de programación con pypy
============================================

PyConAr 2013, Rosario, Argentina

.. class:: hide-title

.
=

::

    21:40 <rogerduran> marianoguerra: "hagamos un lenguaje de programacion
    con pypy", deja de escribir lenguajes =P

.. class:: hide-title

.
=

* efene (py/js lang for the erlang VM)
* erldn (edn parser, erlang)
* squim (scheme, js)
* jsonpath.js (jsonpath, js)
* qrly (jquery selectors for xml/html, erlang)
* fnt (jquery templates, erlang)
* emel (generate html from css selectors, erlang)

Que es PyPy
===========

* Dos cosas
* Implementacion de python (en python, bueh, mas o menos python)
* Toolchain para implementar lenguajes dinámicos con JIT y GC gratis

Que es RPython
==============

* Subset de python

  - Estaticamente tipado (inferencia de tipos)
  - Difuso
  - No muy amigable

* "RPython is everything that our translation toolchain can accept"

* Preguntenme por mi experiencia con rpython al final

Restricciones
=============

* Variables de un solo tipo (o None)
* Variables a nivel modulo se consideran constantes

  - los bindings no pueden cambiar en tiempo de ejecución

* For solo para builtins
* Generadores bastante restringidos
* Strings bastante restringidos
* Mas `aca <http://doc.pypy.org/en/latest/coding-guide.html#object-restrictions>`_

nil-lang
========

Makefile
--------

.. class:: prettyprint lang-make
.. code-block:: make

    all: plang-c

    plang-c:
            @echo "Building Plang"
            ../../pypy/pypy-c ../../pypy/rpython/bin/rpython plang.py

    clean:
            rm plang-c

readinput
---------

.. class:: prettyprint lang-python
.. code-block:: python

    def readinput():
        result = []
        while True:
            s = os.read(0, 1)
            result.append(s)
            if s == '':
                if len(result) > 1:
                    break
                raise SystemExit
        return "".join(result)

entrypoint
----------

.. class:: prettyprint lang-python
.. code-block:: python

    def entry_point(argv):
        input_data = readinput()

        if input_data == "nil\n":
            print "nil"
            return 0
        else:
            print "Error: invalid program '%s'" % input_data
            return -1

    def target(*args):
        return entry_point, None

    if __name__ == "__main__":
        entry_point(sys.argv)

Vocabulario
-----------

* lexer
* parser


Parser
------

.. class:: prettyprint lang-python
.. code-block:: python

    from rply import ParserGenerator, LexerGenerator
    from rply.token import BaseBox

    lg = LexerGenerator()
    lg.add("nil", r"nil")
    lg.ignore(r"[\s,\r\n\t]+")

    lexer = lg.build()
    pg = ParserGenerator(["nil"])

Parser (tipos)
--------------

.. class:: prettyprint lang-python
.. code-block:: python

    class Nil(BaseBox):
        # without this pypy doesn't compile
        def __init__(self):
            BaseBox.__init__(self)

        def to_str(self):
            return "nil"

    nil = Nil()

Parser
------

.. class:: prettyprint lang-python
.. code-block:: python

    @pg.production("main : value")
    def main(state, p):
        return p[0]

    @pg.production("value : nil")
    def value_nil(state, p):
        return nil

    parser = pg.build()

Parser (api y errores)
----------------------

.. class:: prettyprint lang-python
.. code-block:: python

    def loads(code):
        state = State()
        return parser.parse(lexer.lex(code), state)

    @pg.error
    def error_handler(token):
        raise ValueError("Ran into a %s where it wasn't expected" %
             token.gettokentype())


Usamos el parser I
------------------

.. class:: prettyprint lang-diff
.. code-block:: diff

    +import rply.parser
    +import edn

Usamos el parser II
-------------------

.. class:: prettyprint lang-diff
.. code-block:: diff

    -    if input_data == "nil\n":
    -        print "nil"
    -        return 0
    -    else:
    -        print "Error: invalid program '%s'" % input_data

Usamos el parser III
--------------------

.. class:: prettyprint lang-diff
.. code-block:: diff

    +    try:
    +        input_parsed = edn.loads(input_data)
    +        print input_parsed.to_str()
    +    # catching two exceptions here makes pypy fail with a weird error
    +    except rply.parser.ParsingError as error:
    +        pos = error.getsourcepos()
    +        print "Error reading code at line: %d column: %d" % (pos.lineno, pos.colno)
             return -1
    +    except rply.errors.LexingError as error:
    +        pos = error.getsourcepos()
    +        print "Error reading code at line: %d column: %d" % (pos.lineno, pos.colno)
    +        return -1
    +
    +    return 0

Usandolo
--------

.. class:: prettyprint lang-diff
.. code-block:: diff

    make # tasa de cafe

    echo "nil" | ./plang-c
    nil

Booleans
========

true y false al parser
----------------------

.. class:: prettyprint lang-diff
.. code-block:: diff

    +lg.add("true", r"true")
    +lg.add("false", r"false")
     
    -pg = ParserGenerator(["nil"])
    +pg = ParserGenerator(["nil", "true", "false"]) 

Nueva jerarquía
---------------

.. class:: prettyprint lang-diff
.. code-block:: diff

    +# if it doesn't inherith from BaseBox it pypy doesn't compile it
    +class Type(BaseBox):
    +    def __init__(self):
    +        pass
    +
    +    def to_str(self):
    +        return "<type>"

    -class Nil(BaseBox):
    +class Nil(Type):

Tipo
----

.. class:: prettyprint lang-diff
.. code-block:: diff

    +class Bool(Type):
    +    def __init__(self, value):
    +        Type.__init__(self)
    +        self.value = value
    +
    +    def to_str(self):
    +        if self.value:
    +            return "true"
    +        else:
    +            return "false"

    +true = Bool(True)
    +false = Bool(False) 

Nuevos casos
------------

.. class:: prettyprint lang-diff
.. code-block:: diff

    +@pg.production("value : true")
    +def value_true(state, p):
    +    return true
    +
    +@pg.production("value : false")
    +def value_false(state, p):
    +    return false

Números
=======

Tipos
-----

.. class:: prettyprint lang-diff
.. code-block:: diff

    +class Int(Type):
    +    def __init__(self, value):
    +        Type.__init__(self)
    +        self.value = value
    +
    +    def to_str(self):
    +        return "%d" % self.value
    +
    +class Float(Type):
    +    def __init__(self, value):
    +        Type.__init__(self)
    +        self.value = value
    +
    +    def to_str(self):
    +        return "%f" % self.value

Parser
------

.. class:: prettyprint lang-diff
.. code-block:: diff

    +lg.add("float", r"\d+\.\d+")
    +lg.add("number", r"\d+") 

    -pg = ParserGenerator(["nil", "true", "false"])
    +pg = ParserGenerator(["nil", "true", "false", "float", "number"])

    +@pg.production("value : float")
    +def value_float(state, p):
    +    return Float(float(p[0].getstr()))
    +
    +@pg.production("value : number")
    +def value_integer(state, p):
    +    return Int(int(p[0].getstr()))

Strings
=======

Tipo
----

.. class:: prettyprint lang-diff
.. code-block:: diff

    +class Str(Type):
    +    def __init__(self, value):
    +        Type.__init__(self)
    +        self.value = value
    +
    +    def to_str(self):
    +        return '%s' % self.value 

Parser
------

.. class:: prettyprint lang-diff
.. code-block:: diff

    +lg.add("string", r'"(\\\^.|\\.|[^\"])*"') 

    -pg = ParserGenerator([...])
    +pg = ParserGenerator([..., "string"]) 

    +@pg.production("value : string")
    +def value_string(state, p):
    +    return Str(p[0].getstr()) 

Símbolos
========

Tipo
----

.. class:: prettyprint lang-diff
.. code-block:: diff

    +class Symbol(Type):
    +    def __init__(self, value):
    +        Type.__init__(self)
    +        self.value = value
    +
    +    def to_str(self):
    +        return self.value 

Parser
------

.. class:: prettyprint lang-diff
.. code-block:: diff

    +SYMBOL_RE = r"[<>\.\*\/\+\!\-\_\?\$%&=a-zA-Z][<>\.\*\+\!\-\_\?\$%&=a-zA-Z0-9:#]*" 
    +lg.add("symbol", SYMBOL_RE) 

    -pg = ParserGenerator([...])
    +pg = ParserGenerator([..., "symbol"]) 

    +@pg.production("value : symbol")
    +def value_symbol(state, p):
    +    return Symbol(p[0].getstr()) 

Pero...
-------

::

    +    echo "__lang_version__" | ./plang-c
    +    __lang_version__ 

Resolviendo símbolos
====================

Errores
-------

.. class:: prettyprint lang-python
.. code-block:: python

    +class PError(Exception):
    +    def __init__(self, msg):
    +        self.msg = msg
    +
    +    def to_str(self):
    +        return self.msg
    +
    +class PUnboundError(PError):
    +    def __init__(self, msg, name, env):
    +        PError.__init__(self, msg)
    +        self.name = name
    +        self.env = env
    +
    +    def __str__(self):
    +        return "%s: %s" % (self.msg, self.name) 

Env
---

.. class:: prettyprint lang-python
.. code-block:: python

    +class Env(Type):
    +    def __init__(self, bindings):
    +        Type.__init__(self)
    +        self.bindings = bindings
    +
    +    def get(self, name):
    +        # dict.get must take the two args
    +        result = self.bindings.get(name, None)
    +        if result is None:
    +            raise PUnboundError("'%s' not bound" % name, name, self)
    +
    +        return result
    +
    +    def set(self, name, value):
    +        self.bindings[name] = value 

Eval general
------------

.. class:: prettyprint lang-python
.. code-block:: python

    +    def eval(self, env):
    +        return self 


Eval para simbolo
-----------------

.. class:: prettyprint lang-python
.. code-block:: python

    +    def eval(self, env):
    +        return env.get(self.value) 

Cambios para usar env y eval
----------------------------

.. class:: prettyprint lang-python
.. code-block:: python

    +    env = edn.Env({"__lang_version__": edn.Str("0.0.1")})
     
         try:
             input_parsed = edn.loads(input_data)
    -        print input_parsed.to_str()
    +        print input_parsed.eval(env).to_str()
         # catching two exceptions here makes pypy fail with a weird error
         except rply.parser.ParsingError as error:
             pos = error.getsourcepos()
    @@ -31,6 +32,9 @@ def entry_point(argv):
             pos = error.getsourcepos()
             print "Error reading code at line: %d column: %d" % (pos.lineno, pos.colno)
             return -1
    +    except edn.PError as error:
    +        print error.to_str()
    +        return -1 


Pares
=====

Parser
------

.. class:: prettyprint lang-python
.. code-block:: python

    +lg.add("olist", r"\(")
    +lg.add("clist", r"\)") 

    +@pg.production("value : olist clist")
    +def value_empty_list(state, p):
    +    return nil 

    +@pg.production("items : value")
    +def value_items_more(state, p):
    +    return ValueList([p[0]])

    +@pg.production("items : value items")
    +def value_items_more(state, p):
    +    return ValueList([p[0]] + p[1].getitems())

    +@pg.production("value : olist items clist")
    +def value_list(state, p):
    +    return pair_from_iter(p[1].getitems()) 

Tipo
----

.. class:: prettyprint lang-python
.. code-block:: python

    +class Pair(Type):
    +    def __init__(self, head, tail=nil):
    +        self.head = head
    +        self.tail = tail
    +
    +    def __iter__(self):
    +        pair = self
    +        while True:
    +            cur = pair.head
    +            yield cur
    +            if pair.tail == nil:
    +                break
    +            else:
    +                pair = pair.tail
    +                if not isinstance(pair, Pair):
    +                    break
    +
    +    def eval(self, env):
    +        return self
    +
    +    def to_str(self):
    +        return "(%s)" % " ".join([item.to_str() for item in self]) 

Comentarios
-----------

.. class:: prettyprint lang-python
.. code-block:: python

     +lg.ignore(r";.*\n") 

Continuations
=============

Wikipedia dice
--------------

::

    Una continuación es una representación abstracta del estado de un
    programa.

    Una continuación "reifica" el estado del programa, la continuación
    es una estructura de datos que representa el proceso computacional
    en un punto de la ejecución del proceso.

    dicha estructura de datos puede ser accedida por el lenguaje en
    lugar de estar escondida en el runtime.

    Continuaciones son útiles para codificar otros mecanismos de control
    como excepciones, generadores, corutinas entre otros.

Pair.eval
---------

.. class:: prettyprint lang-python
.. code-block:: python

     def eval(self, cc):
    -        return cc.resolve(self)
    +        if cc.do_run:
    +            return Cc(self.head, CallResolver(self, cc), cc.env, cc)
    +        else:
    +            return Cc(self.head, HeadResolver(self, cc), cc.env, cc) 

Continuations
-------------

.. class:: prettyprint lang-python
.. code-block:: python

    +class CallResolver(Resolver):
    ...
    +    def resolve(self, value):
    +        if isinstance(value, Callable):
    +            return value.call(self.val.tail, self.cc)
    +        else:
    +            raise PCallableExpectedError("Callable expected", value)
    
    +class TailResolver(Resolver):
    ...
    +    def resolve(self, tail):
    +        return self.cc.resolve(Pair(self.val, tail))
    +
    +class HeadResolver(Resolver):
    ...
    +    def resolve(self, head):
    +        return Cc(self.val.tail, TailResolver(head, self.cc), self.cc.env,
    +                self.cc, False) 

Mas vocabulario
===============

* operativo

  + do
  + def
  + if
  + lambda (el operativo para crear un lambda)

* aplicativo

  + print

call/cc
=======

Wikipedia dijo...
-----------------

"Continuaciones son útiles para codificar otros mecanismos de control como
excepciones, generadores, corutinas entre otros."

Continuation sandwich
---------------------

::

    Say you're in the kitchen in front of the refrigerator,
    thinking about a sandwich.

    You take a continuation right there and stick it in your pocket.

    Then you get some turkey and bread out of the refrigerator and make
    yourself a
    sandwich, which is now sitting on the counter.

    You invoke the continuation in your pocket, and you find yourself
    standing in front of the refrigerator again, thinking about a sandwich.

    But fortunately, there's a sandwich on the counter, and all the
    materials used to make it are gone. So you eat it. :-)

Ejemplo
-------

.. class:: prettyprint lang-lisp
.. code-block:: lisp

    (def identity (lambda (value) value))

    (def f (lambda (return)
      (return 2)
      3))

    (display (f identity))

    (display (call-cc f))

.. class:: prettyprint lang-python
.. code-block:: python

    def identity(value):
        return value

    def f(ret):
        ret(2)
        return 3

    print(f(identity))

    print(callcc(f)))

Salida?
-------

::

    3
    2

Usos
----

* raise
* break
* continue
* backtracking
* yield


Estado
======

* do
* def
* lambda
* aritmetica (+, -, \*, /)
* logica (<, >, <=, >=, !=, ==)

Futuro
======

* mas operativos
* bootstrap
* $vau

Benchmarks
==========

::

    I forked plang and added few things, just enough to run the TAK
    microbenchmark (ported to the Kernel Language syntax)

       https://github.com/havleoto/plang/blob/master/examples/tak.k

    The TAK is originally one of the classical Lisp benchmarks of
    P. Gabriel. It tests the speed of recursive function calls.

    The execution times:

    (1) plang (interpreted by python 2.7.3) ... 68.74 seconds
    (2) plang (interpreted by pypy 2.1) ........ 5.51 seconds
    (3) plang (compiled by RPython and pypy) ... 0.82 seconds

    compare with Kernel Language interpreters:

    (4) SINK (compiled by chicken 2.732) ..... 111.76 seconds
    (5) klisp 0.3 (default branch) ............. 3.34 seconds
    (6) Bronze Age Lisp (head).................. 0.17 seconds

Benchmarks (cont.)
==================

::

    Usual microbenchmark caveats apply. Also, plang is not really a kernel
    language interpreter (no $vau, no general parameter trees, no guarded
    continuations, no cyclic lists, etc.). Also, I'm not very familiar with
    python and never used pypy before.

    The performance of the compiled plang is quite impressive, considering 
    that it is implemented in a subset of a dynamic language.

    Benchmark details:

       All benchmark were run on Intel(R) Pentium(R) 4 CPU 3.06GHz, 0.5GB RAM,
       with Debian "Wheezy" linux distribution. All software which is not
       mentioned (gcc, libc, ...) comes from Debian.

Benchmarks (cont.)
==================

::

       (1) Run under python 2.7.3 from Debian Wheezy, with rply-0.6.1 parser
           generator library from https://pypi.python.org/pypi/rply/0.6.1.

       (2) Run under pypy-2.1. I used pypy's precompiled binary for x86 linux
           (http://pypy.org/download.html)

       (3) Compiled with RPython compiler from pypy-2.1 source distribution.
           The compiler is run in the precompiled pypy-2.1.

           In this benchmark, plang is NOT compiled with -Ojit. I was not able
           to make -Ojit work (Exception: target has no jitpolicy defined).

Benchmarks (cont.)
==================

::

       (4) SINK is a Kernel Interpreter by John Shutt written in Scheme,
           http://web.cs.wpi.edu/~jshutt/kernel.html,
           version 0.1 m 10, 21 September 2009.

           I've concatenated all source files into one, replaced () with '()
           where necessary,

           and compiled it with Chicken Scheme 2.732 (http://www.call-cc.org/).

       (5) Corresponds to the current head of
           https://bitbucket.org/AndresNavarro/klisp,
           built for "posix" target, USE_LIBFFI=1.

       (6) Corresponds to the current head of
           https://bitbucket.org/havleoto/bronze-age-lisp.

    Best wishes,

       Oto Havle.

Gracias
=======

* Hecho con `rst2html5 <https://github.com/marianoguerra/rst2html5>`_
* `plang <https://github.com/marianoguerra/plang/commits/master>`_

Preguntas
=========
