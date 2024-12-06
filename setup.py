from setuptools import setup, Extension
from Cython.Build import cythonize

ext_modules = [
    Extension(
        "wator.draw",
        ["src/wator/draw.py"],
        extra_compile_args=["/arch:AVX512", "/O2"],
        define_macros=[("CYTHON_LIMITED_API", "1")],
        py_limited_api=True,
    )
]

setup(ext_modules=cythonize(ext_modules, annotate=True))