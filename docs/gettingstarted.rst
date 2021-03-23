********************************************************************************
Getting Started
********************************************************************************

Installation
============

``compas_cgal`` can be installed via ``conda-forge``.

.. code-block:: bash

    conda create -n cgal -c conda-forge python=3.8 compas compas_cgal

Optional requirements
=====================

Several examples use COMPAS View2 for visualisation outside of CAD environments.
To install ``compas_view2`` in the same environment

.. code-block:: bash

    conda install -n cgal -c conda-forge compas_view2

Or everything in one go

.. code-block:: bash

    conda create -n cgal -c conda-forge compas compas_cgal compas_view2
