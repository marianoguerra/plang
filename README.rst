plang
=====

oh noes, yet another language!

plang is a simple scheme/clojure/kernel like programming language implemented
using pypy.

why? oh for $DEITY's sake why?
------------------------------

started as material for a talk I will be giving at Pycon Argentina 2013

how?
----

compile with make::

    make

the interpreter reads the program from the standard input::

    echo "(println 42 name true 1.2 answer nil (list 1 2 3))" | ./plang-c

    In:  (println 42 name true 1.200000 answer nil (list 1 2 3))
    (42 :bob true 1.200000 42 nil (1 2 3))
    Res: nil

who?
----

marianoguerra

license
-------

GPLv3 + optional beer 
