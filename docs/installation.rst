********************************************************************************
Installation
********************************************************************************

Stable
======

Stable releases of :mod:`compas_cgal` can be installed via `conda-forge`.

.. code-block:: bash

    conda create -n cgal -c conda-forge compas compas_cgal --yes
    conda activate cgal


Optional
========

Several examples use COMPAS View2 for visualisation outside of CAD environments.
To install :mod:`compas_view2` in the same environment

.. code-block:: bash

    conda install compas_view2 --yes

Or everything in one go

.. code-block:: bash

    conda create -n cgal -c conda-forge compas compas_cgal compas_view2 --yes


Dev Install
===========

A local development version can be set up using a combination of `conda` and `pip`.
First, clone the :mod:`compas_cgal` repo.

.. code-block:: bash

    git clone https://github.com/compas-dev/compas_cgal


Create an environment with all the required dependencies.

.. raw:: html

    <div class="card">
        <div class="card-header">
            <ul class="nav nav-tabs card-header-tabs">
                <li class="nav-item">
                    <a class="nav-link active" data-toggle="tab" href="#dev_windows">Windows</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" data-toggle="tab" href="#dev_unix">OSX / Linux</a>
                </li>
            </ul>
        </div>
        <div class="card-body">
            <div class="tab-content">

.. raw:: html

    <div class="tab-pane active" id="dev_windows">

.. code-block:: bash

    conda create -n cgal-dev python=3.8 mpir mpfr boost-cpp eigen=3.3 cgal-cpp=5.2 pybind11 compas compas_view2 --yes

.. raw:: html

    </div>
    <div class="tab-pane" id="dev_unix">

.. code-block:: bash

    conda create -n cgal-dev python=3.8 mpfr gmp boost-cpp eigen=3.3 cgal-cpp=5.2 pybind11 compas compas_view2 --yes

.. raw:: html

    </div>

.. raw:: html

    </div>
    </div>
    </div>

Activate the environment.

.. code-block:: bash

    conda activate cgal-dev


Change to the root folder of the :mod:`compas_cgal` repo.

.. code-block:: bash

    cd compas_cgal


And compile the code while creating an editable install of the python wrapper using `setuptools`.

.. code-block:: bash

    pip install -e .


To add your c++ module to the wrapper, and potentially exclude some of the existing modules during its development,
modify the list of extension modules in the `setup.py` file.

.. code-block:: python

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
