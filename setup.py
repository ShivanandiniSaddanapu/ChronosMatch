from setuptools import Extension, setup
from Cython.Build import cythonize

extensions = [
    Extension(
        "chronosmatch.matching.cython.match_core",
        ["src/chronosmatch/matching/cython/match_core.pyx"],
    )
]

setup(
    ext_modules=cythonize(
        extensions,
        compiler_directives={"language_level": "3"},
    )
)
