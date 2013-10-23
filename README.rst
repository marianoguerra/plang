try with python::

    cat examples/nil.nilang | python plang.py

    nil

try with compiled pypy::

    cat examples/nil.nilang | ./plang-c

    nil

make it fail::

    echo "stuff" | ./plang-c

    Error: invalid program 'stuff
    '
