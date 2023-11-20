.. _devguide:

********************************************************************************
Development Guide
********************************************************************************

Environment
===========

To set up a local development environment, start by cloning the :mod:`compas_cgal` repo.

.. code-block:: bash

    git clone https://github.com/compas-dev/compas_cgal

Then, create an environment with all requirements using the provided environment file.
The requirements are slightly different on Windows...

.. tab-set::

    .. tab-item:: OSX
        :selected:

        .. code-block:: bash

            cd compas_cgal
            conda env create -f env_osx.yml

    .. tab-item:: Windows

        .. code-block:: bash

            cd compas_cgal
            conda env create -f env_win.yml

Note, that this will immediately also build :mod:`compas_cgal` for your system.


Build
=====

To manually build the extension modules,
for example after making changes to one of the extension modules or adding a new one,
simply run the ``setup.py`` file trough a local source install.

.. code-block:: bash

    pip install -e .


Extension modules
=================

To control which extension modules are built,
modify the list of extension modules in the ``setup.py`` file,
and the corresponding declaration and initialisation of modules in ``src/compas_cgal.cpp``.
``src/compas_cgal.cpp`` is the entry point for all extension modules.
``src/compas.cpp`` defines common functionality for all extension modules.
They should not be removed.

.. code-block:: python

    # setup.py

    ext_modules = [
        Extension(
            'compas_cgal._cgal',
            sorted([
                'src/compas_cgal.cpp',
                'src/compas.cpp',
                'src/meshing.cpp',
                'src/booleans.cpp',
                'src/slicer.cpp',
                'src/intersections.cpp',
                'src/measure.cpp',
                'src/triangulations.cpp',
                'src/subdivision.cpp',
            ]),
            include_dirs=[
                './include',
                get_eigen_include(),
                get_pybind_include()
            ],
            library_dirs=[
                get_library_dirs(),
            ],
            libraries=['mpfr', 'gmp'],
            language='c++'
        ),
    ]

.. code-block:: cpp

    // src/compas_cgal.cpp

    #include <pybind11/pybind11.h>
    #include <compas.h>


    // here all modules of "_cgal" are declared.
    void init_meshing(pybind11::module&);
    void init_booleans(pybind11::module&);
    void init_slicer(pybind11::module&);
    void init_intersections(pybind11::module&);
    void init_measure(pybind11::module&);
    void init_triangulations(pybind11::module&);
    void init_subdivision(pybind11::module&);


    // the first parameter here ("_cgal") will be the name of the "so" or "pyd" file that will be produced by PyBind11
    // which is the entry point from where all other modules will be accessible.
    PYBIND11_MODULE(_cgal, m) {
        m.doc() = "";

        // register Result as a Python class
        pybind11::class_<compas::Result>(m, "Result")
            .def_readonly("vertices", &compas::Result::vertices)
            .def_readonly("faces", &compas::Result::faces);

        // here all modules of "_cgal" are initializied.
        init_meshing(m);
        init_booleans(m);
        init_slicer(m);
        init_intersections(m);
        init_measure(m);
        init_triangulations(m);
        init_subdivision(m);
    }


Example
=======

Coming soon!


Include Path
============

To avoid having VS Code complain about missing includes, add the following to ``.vscode/c_cpp_properties.json``.

.. code-block:: json

    {
        "configurations": [
            {
                ...
                "includePath": [
                    "${workspaceFolder}/**",
                    "/path/to/(mini)conda/envs/cgal-dev/include",
                    "/path/to/(mini)conda/envs/cgal-dev/include/python3.9",
                    "/path/to/(mini)conda/envs/cgal-dev/include/eigen3"
                ],
                ...
            },
        ...
    }

Replace ``/path/to/(mini)conda`` with the actual path to your (mini)conda installation.
