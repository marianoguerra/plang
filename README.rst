try with python::

    cat examples/nil.nilang | python plang.py

    nil

try with compiled pypy::

    echo "nil" | ./plang-c
    nil

    echo "true" | ./plang-c
    true
    
    echo "false" | ./plang-c
    false

make it fail::

    echo "stuff" | ./plang-c
    Error reading code at line: -1 column: -1
