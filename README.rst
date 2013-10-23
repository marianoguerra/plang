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

    echo "42.3" | ./plang-c
    42.300000

    echo "42" | ./plang-c
    42

    echo '"hello"' | ./plang-c
    "hello"

    echo '"he\"ll\"o"' | ./plang-c
    "he\"ll\"o"

    echo "__lang_version__" | ./plang-c
    __lang_version__

make it fail::

    echo "stuff" | ./plang-c
    Error reading code at line: -1 column: -1
