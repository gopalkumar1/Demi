from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [
	Extension("Generic_Call", ["Generic_Call.py"]),
	Extension("main", ["main.py"]),

	#   ... all your modules that need be compiled ...
]
setup(
	name='test_py_pack',
	cmdclass={'build_ext': build_ext},
	ext_modules=ext_modules
)
