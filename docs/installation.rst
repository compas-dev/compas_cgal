********************************************************************************
Installation
********************************************************************************

Stable
======

Stable releases of :mod:`compas_cgal` can be installed via ``conda-forge``.

.. code-block:: bash

    conda create -n cgal -c conda-forge compas_cgal

Several examples use the COMPAS Viewer for visualisation.
To install :mod:`compas_view2` in the same environment

.. code-block:: bash

    conda activate cgal
    conda install compas_view2

Or everything in one go

.. code-block:: bash

    conda create -n cgal -c conda-forge compas_cgal compas_view2

Dev Install
===========

See :doc:`devguide`.
