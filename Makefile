
all: plang-c

plang-c:
	@echo "Building Plang with JIT"
	../../pypy/rpython/bin/rpython plang.py

plang-c-jit:
	@echo "Building Plang with JIT"
	../../pypy/rpython/bin/rpython -Ojit plang.py
