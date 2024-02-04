from setuptools import setup
from Cython.Build import cythonize

setup(
    name="FrameBuffer Module",
    ext_modules=cythonize("frame_buffer.pyx"),
    zip_safe=False,
)
