import os
import tempfile

import setuptools
from setuptools import Extension
from setuptools import setup
from setuptools.command.build_ext import build_ext

conda_prefix = os.getenv("CONDA_PREFIX")

windows = os.name == "nt"


def get_pybind_include():
    if windows:
        return os.path.join(conda_prefix, "Library", "include")
    return os.path.join(conda_prefix, "include")


def get_eigen_include():
    if windows:
        return os.path.join(conda_prefix, "Library", "include", "eigen3")
    return os.path.join(conda_prefix, "include", "eigen3")


def get_library_dirs():
    if windows:
        return os.path.join(conda_prefix, "Library", "lib")
    return os.path.join(conda_prefix, "lib")


def get_scip_library():
    if windows:
        return "libscip"
    return "scip"


ext_modules = [
    Extension(
        "compas_cgal._cgal",
        sorted(
            [
                "src/compas_cgal.cpp",
                "src/compas.cpp",
                "src/meshing.cpp",
                "src/booleans.cpp",
                "src/slicer.cpp",
                "src/intersections.cpp",
                "src/measure.cpp",
                "src/subdivision.cpp",
                "src/triangulations.cpp",
                "src/skeletonization.cpp",
                "src/reconstruction.cpp",
                "src/polygonal_surface_reconstruction.cpp",
            ]
        ),
        include_dirs=["./include", get_eigen_include(), get_pybind_include()],
        library_dirs=[get_library_dirs()],
        libraries=["mpfr", "gmp", get_scip_library()],
        language="c++",
    ),
]


# cf http://bugs.python.org/issue26689
def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    with tempfile.NamedTemporaryFile("w", suffix=".cpp", delete=False) as f:
        f.write("int main (int argc, char **argv) { return 0; }")
        fname = f.name
    try:
        compiler.compile([fname], extra_postargs=[flagname])
    except setuptools.distutils.errors.CompileError:
        return False
    finally:
        try:
            os.remove(fname)
        except OSError:
            pass
    return True


def cpp_flag(compiler):
    """Return the -std=c++[11/14/17] compiler flag.

    The newer version is prefered over c++11 (when it is available).
    """
    flags = ["-std=c++14", "-std=c++11"]

    for flag in flags:
        if has_flag(compiler, flag):
            return flag

    raise RuntimeError("Unsupported compiler -- at least C++11 support " "is needed!")


class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""

    c_opts = {
        "msvc": ["/EHsc", "/std:c++14"],
        "unix": [],
    }
    l_opts = {
        "msvc": [],
        "unix": [],
    }

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        link_opts = self.l_opts.get(ct, [])
        if ct == "unix":
            opts.append('-DVERSION_INFO="%s"' % self.distribution.get_version())
            opts.append(cpp_flag(self.compiler))
            if has_flag(self.compiler, "-fvisibility=hidden"):
                opts.append("-fvisibility=hidden")
            opts.append("-DCGAL_DEBUG=1")
        for ext in self.extensions:
            ext.define_macros = [("VERSION_INFO", '"{}"'.format(self.distribution.get_version()))]
            ext.extra_compile_args = opts
            ext.extra_link_args = link_opts
        build_ext.build_extensions(self)


setup(
    name="compas_cgal",
    packages=["compas_cgal"],
    ext_modules=ext_modules,
    cmdclass={"build_ext": BuildExt},
)
