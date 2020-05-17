# COMPAS CGAL

COMPAS friedly bindings for the CGAL library.

## Installation

**This has only been tested on Mac.**

```bash
conda create -n cgal python=3.7 python.app eigen boost-cpp cgal-cpp">=5.0" pybind11 COMPAS --yes
conda activate cgal
pip install -e .
```

```bash
python ./scripts/test_hello.py
Hello COMPAS
0
```

```bash
python ./scripts/test_mesh.py
         6052 function calls (6003 primitive calls) in 0.275 seconds

   Ordered by: internal time
   List reduced from 431 to 10 due to restriction <10>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        2    0.093    0.047    0.093    0.047 {method 'do_handshake' of '_ssl._SSLSocket' objects}
        4    0.068    0.017    0.068    0.017 {method 'read' of '_ssl._SSLSocket' objects}
        2    0.066    0.033    0.066    0.033 {method 'connect' of '_socket.socket' objects}
        2    0.022    0.011    0.022    0.011 {method 'set_default_verify_paths' of '_ssl._SSLContext' objects}
        1    0.006    0.006    0.006    0.006 {built-in method _scproxy._get_proxies}
        2    0.005    0.002    0.005    0.003 socket.py:652(close)
        2    0.003    0.002    0.005    0.003 {built-in method _socket.getaddrinfo}
       12    0.003    0.000    0.003    0.000 {built-in method __new__ of type object at 0x105c70288}
      244    0.000    0.000    0.000    0.000 {method 'lower' of 'str' objects}
        4    0.000    0.000    0.001    0.000 sre_compile.py:276(_optimize_charset)

```
