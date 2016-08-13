import sys
from ctypes import *
from math import isfinite

c = compile('0+({}{})'.format('\\\n' * 255, sys.argv[1]), '', 'eval')
code = c.co_code
consts = c.co_consts

ops = {
    10: (0, b''),
    11: (0, b'\xd9\xe0'),
    23: (0, b'\xde\xc1'),
    27: (0, b'\xde\xf9'),
    24: (0, b'\xde\xe9'),
    20: (0, b'\xde\xc9'),
    83: (0, b'\xdd\x5d\xf0\xf2\x0f\x10\x45\xf0\x5d\xc3'),
    100: (1, lambda x: b'\x48\x8b\x45\xf8\x48\x83\xc0' + bytes([x * 8]) + b'\xdd\x00'),
}
buf = b'\x55\x48\x89\xe5\x48\x89\x7d\xf8'
while code:
    arity, op = ops[code[0]]
    code = code[1:]
    if arity:
        op = op(code[0] + (code[1] << 8))
        code = code[2:]
    buf += op

libc = CDLL('libc.so.6')
size = len(buf)
addr = memmove(libc.valloc(size), buf, size)
libc.mprotect(addr, size, 7)
consts_t = c_double * len(consts)
f = cast(addr, CFUNCTYPE(c_double, consts_t))
n = f(consts_t(*consts))
assert isfinite(n)
print(n)
