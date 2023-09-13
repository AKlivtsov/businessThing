from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [
    Extension("ver1_3.main", ["main.py"])
    ]

setup(
    name = 'Test App',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)