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

    echo "woot" | ./plang-c
    'woot' not bound

    echo "__lang_version__" | ./plang-c
    0.0.1

    echo "()" | ./plang-c
    nil

    echo '(1 2.3 false nil "asd")' | ./plang-c
    (1 2.300000 false nil "asd")

    echo '(display 1 2.3 false nil "asd" (dump __lang_version__)) ; comment' | ./plang-c
    dump: (__lang_version__)
    (1 2.300000 false nil "asd" nil)
    nil

    echo '(display 1 2.3 false nil "asd" (display __lang_version__)) ; comment' | ./plang-c
    (0.0.1)
    (1 2.300000 false nil "asd" nil)
    nil

    echo "((lambda (x) x) 42)" | ./plang-c
    42

    echo '(display "hi") 42 "end"' | ./plang-c
    ("hi")
    "end"

    echo '(def name "bob") (display "hi" name) 42 "end"' | ./plang-c
    ("hi" "bob")
    "end"

make it fail::

    echo "stuff" | ./plang-c
    Error reading code at line: -1 column: -1
