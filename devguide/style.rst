********************************************************************************
Style
********************************************************************************

Python Code
===========

Use the compas style guide from the offcial documentation `documentation <https://compas.dev/compas/latest/devguide/code.html>`_.


C++ Code
========

* Functions: ``snake_case``
* Variables (local and public): ``snake_case``
* Private members: ``_snake_case`` (prefix with _)
* Static members: ``s_snake_case`` (prefix with s and _)
* Constants: ``SNAKE_UPPER_CASE``
* Class/Struct names: ``UpperCamelCase``

Namespaces
----------

.. code-block:: cpp

    // Do not use "using namespace std", specify namespace explicitly
    std::vector<double> points;

Functions
---------

.. code-block:: cpp

    // Next line bracket style
    void compute_boolean_union()
    {
        /* content */
    }

Structures
----------

.. code-block:: cpp

    // Structure name uses UpperCamelCase
    struct MeshData
    {
        // Structure attribute uses snake_case
        const char* file_name;
    };


Classes
-------

.. code-block:: cpp

    // Class name uses UpperCamelCase
    class BooleanSolver
    {
    public:
        BooleanSolver(const double& tolerance);
        virtual ~BooleanSolver();

        // Member functions use snake_case
        void compute_intersection()
        {
            // Local variable uses snake_case
            double tolerance = 0.001;
        }

    // Field indicator to separate functions and attributes
    public:
        int result_count;      // Public member uses snake_case

    private:
        void validate_mesh();  // Private function uses snake_case
        double _tolerance;     // Private member uses _snake_case
        static int s_meshes;   // Static member uses s_snake_case
        const int MAX_COUNT = 100;  // Constant uses SNAKE_UPPER_CASE
    };

Docstrings
==========

Use Doxygen-style comments with the following format:

Functions and Methods
---------------------

.. code-block:: cpp

    /**
     * @brief Short description of function
     * @param[in] param1 Description of input parameter
     * @param[out] param2 Description of output parameter
     * @return Description of return value
     * @throws Description of potential exceptions
     */
    double compute_intersection(const Mesh& mesh1, Mesh& result);

Classes
-------

.. code-block:: cpp

    /**
     * @brief Short description of class
     * @details Longer description if needed
     */
    class BooleanSolver {
    public:
        /**
         * @brief Constructor description
         * @param tolerance Mesh tolerance value
         */
        BooleanSolver(double tolerance);
    };

Member Variables
----------------

.. code-block:: cpp

    class BooleanSolver {
    private:
        double _tolerance;  //!< Brief description of member variable
        int s_meshes;      //!< Use //!< for single-line member documentation
    };