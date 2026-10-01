********************************************************************************
Types
********************************************************************************

Type Conversion
===============

Matching C++/Python types often takes the most of the time and requires careful attention. When implementing C++/Python bindings, follow these key patterns from the existing files or implement your own. If there are specific types you want to implement, review the `nanobind tests <https://github.com/wjakob/nanobind/tree/master/tests>`_ . Ask questions in discussion section for nanobind typing or follow previous issues. Current implementation provides examples for the following types:


* C++:
    * Use ``Eigen::Ref`` for matrix parameters, e.g. to transfer mesh vertex coordinates.
    * Return complex data as ``std::tuple<type, ...>`` types.
    * Use ``std::vector<type>`` for list copies otherwise use ``const std::vector<type> &``.
    * Use Eigen Matrix types in vectors ``const std::vector<Eigen::Matrix<type, ...>> &`` instead of reference type ``const std::vector<Eigen::Ref<...>> &``.

* Python:
    * Use ``float64`` for vertices and ``int32`` for faces in numpy arrays
    * Enforce row-major (C-contiguous) order for matrices



Type Conversion Patterns
========================

When implementing C++/Python bindings, follow these established patterns:

Matrix Operations
-----------------

Use ``Eigen::Ref`` for efficient matrix passing:

.. code-block:: cpp

    void my_function(const Eigen::Ref<const RowMatrixXd>& vertices,
                    const Eigen::Ref<const RowMatrixXi>& faces);

Return complex mesh data as tuples:

.. code-block:: cpp

    return std::tuple<RowMatrixXd, RowMatrixXi> my_function();

Enforce proper numpy array types using float64 and int32 in C-contiguous order:

.. code-block:: python
    
    import numpy as np
    from compas_cgal.compas_cgal_ext import my_submodule

    # Convert mesh vertices and faces to proper numpy arrays
    vertices1 = np.asarray(mesh1.vertices, dtype=np.float64)
    faces1 = np.asarray(mesh1.faces, dtype=np.int32)

    # Pass to C++ function
    V, F = my_submodule.my_function(vertices1, faces1)
    


Vector Types
------------

For list data, choose between ``std::vector`` for value copies, ``const std::vector&`` for references, and ``std::vector<Eigen::Matrix<type, ...>>`` for matrix vectors.

Bind vector types explicitly:

.. code-block:: cpp

    // In module initialization
    nb::bind_vector<std::vector<double>>(m, "VectorDouble");

Access in Python:

.. code-block:: python

    # Get vector result
    vector_result = my_function()
    # Access elements by index
    x, y, z = vector_result[0], vector_result[1], vector_result[2]

Follow existing patterns: ``booleans.cpp``: Matrix and tuple handling, ``measure.cpp``: Array type validation, ``reconstruction.cpp``: Complex data structures, ``skeletonization.cpp``: Point cloud data, ``slicer.cpp``: Geometry validation

Type Conversion Best Practices
==============================

When implementing new functionality:

* Matrix Operations:

  .. code-block:: cpp

      // GOOD: Use Eigen::Ref for matrix parameters
      void my_function(Eigen::Ref<const RowMatrixXd> vertices);

      // BAD: Don't use raw matrices
      void my_function(Eigen::MatrixXd vertices);

* Return Types:

  .. code-block:: cpp

      // GOOD: Return complex data as tuples
      std::tuple<RowMatrixXd, RowMatrixXi> my_mesh_operation();

      // BAD: Don't use output parameters
      void my_mesh_operation(RowMatrixXd& out_vertices);

* Vector Handling:

  .. code-block:: cpp

      // GOOD: Use const references for input vectors
      void my_function(const std::vector<double>& input);

      // GOOD: Return vectors by value
      std::vector<double> MyOperation();

      // BAD: Don't use non-const references
      void my_function(std::vector<double>& input);

* Matrix Vectors:

  .. code-block:: cpp

      // GOOD: Use Matrix types in vectors
      std::vector<Eigen::Matrix<double, 3, 1>> points;

      // BAD: Don't use Ref types in vectors
      std::vector<Eigen::Ref<Eigen::Vector3d>> points;

* Python Integration:

  .. code-block:: python

      # GOOD: Enforce proper types
      vertices = np.array(points, dtype=np.float64)
      faces = np.array(indices, dtype=np.int32)

      # BAD: Don't rely on automatic conversion
      vertices = points  # type not enforced
      faces = indices   # type not enforced

* Error Handling:

  .. code-block:: cpp

      // GOOD: Validate and throw with clear messages
      if (!IsMeshClosed(vertices, faces)) {
          throw std::runtime_error(
              "Mesh must be closed for boolean operations"
          );
      }

      // BAD: Don't silently handle errors
      if (!IsMeshClosed(vertices, faces)) {
          return std::make_tuple(vertices, faces);  // original input
      }
