********************************************************************************
Contribute
********************************************************************************

Getting Started
===============

Fork the repository to your GitHub account and clone it:

.. code-block:: bash

    git clone https://github.com/<username>/compas_cgal.git 
    cd compas_cgal

Create and switch to a development branch:

.. code-block:: bash

    git branch <branch_name>
    git checkout <branch_name>


Binding Process
===============

C++ Binding
-----------

Create new files in the ``src`` folder:

.. code-block:: bash

    cd src
    touch new_module.cpp
    touch new_module.h

Define new methods declarations in ``src/new_module.h``:

.. code-block:: cpp

    #pragma once

    #include "compas.h"

    // Your method declarations here

Implement the functions and add the nanobind module registration: ``src/new_module.cpp``:

.. code-block:: cpp

    #include "new_module"

    // Your method definitions here

    void init_new_module(nb::module_& m) {
        auto submodule = m.def_submodule("new_module");

        submodule.def(
            "python_function_name",
            &cpp_function_name,
            "description",
            "my_argument1"_a,
            "my_argument2"_a,
        );
    }

Add the submodule registration to ``src/compas_cgal.cpp``:

.. code-block:: cpp

    #include "compas.h"

    ...
    init_new_module(m);
    ...

    NB_MODULE(compas_cgal_ext, m) {
        ...
        init_new_module(m);
    }

Rebuild the project with:

.. code-block:: bash

    pip install --no-build-isolation -ve . -Ceditable.rebuild=true


.. note:: 
    It is advisable to include all the headers from 3rd-party libraries to the precompiled header ``src/compas.h`` so that your compilation time decreases.

Python Binding
--------------

Add the new python submodule in ``src/compas_cgal/__init__.py``:

.. code-block:: python

    __all_plugins__ = [
        ...
        "compas_cgal.new_module",
    ]

Implement the submodule in ``src/compas_cgal/new_module.py``:

.. code-block:: python

    from compas_cgal.compas_cgal_ext import new_module

    def new_function():
        ...
        result_from_cplusplus = new_module.python_function_name()
        ...


After creating new source files, you must rebuild the project with:

.. code-block:: bash

    pip install --no-build-isolation -ve .



Document, Test, and Format
==========================

Documentation
-------------

Document your scripts with a screenshot in ``docs/examples``. Documentation can be build with:

.. code-block:: bash

    invoke docs


Scripts should be profiled for performance checks:

.. code-block:: bash

    pip install line_profiler
    kernprof -l -v -r <path_to_script>

Add a description of the changes in ``CHANGELOG.md``.

.. code-block:: markdown

    ## [1.0.1] 2025-03-06

    ### Added

    * Nanobind integration.

    ### Changed

    ### Removed

Testing
-------

Write tests in the ``tests`` folder and run with pytest. As a bare minimum add a simplest possible test, this will help you run all the tests to know if everything is working.

.. code-block:: bash

    invoke test


Formatting
----------

Run the formatter to ensure consistent code style:

.. code-block:: bash

    invoke format
    invoke lint



GitHub Pull Request
===================

Push the changes to your forked repository:

.. code-block:: bash

    git add --all
    git commit -m "commit message"
    git push origin <branch_name>

Afterwards there should be a green button on GitHub to open a pull request. Check if all the GitHub tasks run successfully. Lastly, as for a review of your code, assign a reviewer at the top left corner of the pull request and wait for the review and make the necessary changes. One of the reviewers will merge your pull request.