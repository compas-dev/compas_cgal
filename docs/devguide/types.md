# Types

## Public Inputs and Native Arrays

Python callers may provide coordinates and indices using ordinary lists,
tuples, COMPAS geometry objects, or NumPy arrays. Public wrapper signatures use
the shared duck-typed vocabulary from `compas.typing`:

- `PointsLike` accepts coordinate collections and numeric arrays.
- `IndicesLike` accepts one-dimensional index containers and integer arrays,
  including fixed-vertex selections used by dual remeshing.
- `IndexGroupsLike` accepts nested index sequences and integer arrays.
- `VerticesFaces` combines those structures without implying a COMPAS `Mesh`
  object or a specific face arity.

These core aliases describe values accepted by Python wrappers; they do not
require a particular NumPy dtype, memory layout, or mutability. The concrete
aliases in `compas_cgal.types`, including `VerticesNumpy`, `FacesNumpy`, and
`VerticesFacesNumpy`, describe normalized native inputs and exact results.
Wrapper boundaries convert compatible public inputs once to the dtype and
memory layout required by the native operation. Every private extension module
has a packaged `.pyi` describing that narrower ABI.

Result aliases retain operation-specific dimensions where they are part of the
contract. Triangle operations return `VerticesFacesNumpy`; Catmull-Clark
subdivision returns `VerticesQuadsNumpy`; and `PolylinesNumpy` contains Nx2 or
Nx3 arrays according to the dimensionality of the input operation.

Several native functions return nanobind vector classes rather than built-in
Python lists. Their stubs name the exact vector class. Public result aliases
describe the shared structural behavior so callers can iterate and index these
results without depending on a private extension class. Wrappers that promise a
list, such as `mesh_centroid`, perform that conversion before returning.

Do not add nominal runtime checks merely to enforce a type annotation. Validate
only semantic requirements of an operation, and let boundary conversion handle
compatible Python and NumPy representations.

## Type Conversion

Matching C++/Python types often takes the most of the time and requires
careful attention. When implementing C++/Python bindings, follow these
key patterns from the existing files or implement your own. If there are
specific types you want to implement, review the [nanobind
tests](https://github.com/wjakob/nanobind/tree/master/tests) . Ask
questions in discussion section for nanobind typing or follow previous
issues. Current implementation provides examples for the following
types:

- C++:  
  - Use `Eigen::Ref` for matrix parameters, e.g. to transfer mesh vertex
    coordinates.
  - Return complex data as `std::tuple<type, ...>` types.
  - Use `std::vector<type>` for list copies otherwise use
    `const std::vector<type> &`.
  - Use Eigen Matrix types in vectors
    `const std::vector<Eigen::Matrix<type, ...>> &` instead of reference
    type `const std::vector<Eigen::Ref<...>> &`.

- Python:  
  - Use `float64` for vertices and `int32` for faces in numpy arrays
  - Enforce row-major (C-contiguous) order for matrices

## Type Conversion Patterns

When implementing C++/Python bindings, follow these established
patterns:

### Matrix Operations

Use `Eigen::Ref` for efficient matrix passing:

``` cpp
void my_function(const Eigen::Ref<const RowMatrixXd>& vertices,
                const Eigen::Ref<const RowMatrixXi>& faces);
```

Return complex mesh data as tuples:

``` cpp
return std::tuple<RowMatrixXd, RowMatrixXi> my_function();
```

Enforce proper numpy array types using float64 and int32 in C-contiguous
order:

``` python
import numpy as np
from compas_cgal import _my_submodule

# Convert mesh vertices and faces to proper numpy arrays
vertices1 = np.asarray(mesh1.vertices, dtype=np.float64)
faces1 = np.asarray(mesh1.faces, dtype=np.int32)

# Pass to C++ function
V, F = _my_submodule.my_function(vertices1, faces1)
```

### Vector Types

For list data, choose between `std::vector` for value copies,
`const std::vector&` for references, and
`std::vector<Eigen::Matrix<type, ...>>` for matrix vectors.

Bind vector types explicitly:

``` cpp
// In module initialization
nb::bind_vector<std::vector<double>>(m, "VectorDouble");
```

Access in Python:

``` python
# Get vector result
vector_result = my_function()
# Access elements by index
x, y, z = vector_result[0], vector_result[1], vector_result[2]
```

Follow existing patterns: `booleans.cpp`: Matrix and tuple handling,
`measure.cpp`: Array type validation, `reconstruction.cpp`: Complex data
structures, `skeletonization.cpp`: Point cloud data, `slicer.cpp`:
Geometry validation

## Type Conversion Best Practices

When implementing new functionality:

- Matrix Operations:

  ``` cpp
  // GOOD: Use Eigen::Ref for matrix parameters
  void my_function(Eigen::Ref<const RowMatrixXd> vertices);

  // BAD: Don't use raw matrices
  void my_function(Eigen::MatrixXd vertices);
  ```

- Return Types:

  ``` cpp
  // GOOD: Return complex data as tuples
  std::tuple<RowMatrixXd, RowMatrixXi> my_mesh_operation();

  // BAD: Don't use output parameters
  void my_mesh_operation(RowMatrixXd& out_vertices);
  ```

- Vector Handling:

  ``` cpp
  // GOOD: Use const references for input vectors
  void my_function(const std::vector<double>& input);

  // GOOD: Return vectors by value
  std::vector<double> MyOperation();

  // BAD: Don't use non-const references
  void my_function(std::vector<double>& input);
  ```

- Matrix Vectors:

  ``` cpp
  // GOOD: Use Matrix types in vectors
  std::vector<Eigen::Matrix<double, 3, 1>> points;

  // BAD: Don't use Ref types in vectors
  std::vector<Eigen::Ref<Eigen::Vector3d>> points;
  ```

- Python Integration:

  ``` python
  # GOOD: Enforce proper types
  vertices = np.array(points, dtype=np.float64)
  faces = np.array(indices, dtype=np.int32)

  # BAD: Don't rely on automatic conversion
  vertices = points  # type not enforced
  faces = indices  # type not enforced
  ```

- Error Handling:

  ``` cpp
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
  ```
