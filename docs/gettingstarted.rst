********************************************************************************
Getting Started
********************************************************************************

Installation
============

On Mac
------

.. code-block:: bash

    conda create -n cgal python=3.7 python.app eigen boost-cpp gmp mpfr cgal-cpp">=5.0" pybind11 COMPAS">=0.16.0"
    conda activate cgal
    pip install -e .

On Windows
----------

.. code-block:: bash

    conda create -n cgal python=3.7 eigen boost-cpp mpir mpfr cgal-cpp">=5.0" pybind11 COMPAS">=0.16.0"
    conda activate cgal
    pip install -e .


Viewers
=======

To install the viewers for CAD independent visualisation, please follow the instructions available here:
https://github.com/compas-dev/compas_viewers
