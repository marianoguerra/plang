
all: plang-c

plang-c:
	@echo "Building Plang"
	../../pypy/pypy-c ../../pypy/rpython/bin/rpython plang.py

clean:
	rm plang-c
