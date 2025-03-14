Type Conversion with Nanobind
=============================

This example demonstrates proper type conversion patterns between C++ and Python using nanobind in COMPAS CGAL.

Key Features:

* Basic type conversion (integers)
* Matrix passing with Eigen::Ref (in-place modification)
* Matrix creation in C++ and transfer to Python
* Row-major order matrix handling
* Proper numpy array type handling (float64)

.. note::
   This example follows the type conversion guidelines:
   
   * Uses row-major order for matrix operations
   * Handles numpy arrays with proper data types
   * Demonstrates both input and output matrix conversions
   * Shows in-place matrix modification patterns

.. literalinclude:: example_nanobind_types.py
   :language: python
