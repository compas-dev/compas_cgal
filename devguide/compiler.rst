********************************************************************************
Compiler Requirements
********************************************************************************

Before installing COMPAS CGAL, you need to ensure you have the appropriate C++ compiler setup for your operating system:

Windows
-------

* Install Visual Studio Build Tools (2022 or newer)
* During installation, select "Desktop development with C++"
* No additional PATH settings are required as CMake will automatically find the compiler

macOS
-----

* Install Xcode Command Line Tools:

  .. code-block:: bash

      xcode-select --install

* The clang compiler will be automatically available after installation

Linux
-----

* Install GCC and related build tools. On Ubuntu/Debian:

  .. code-block:: bash

      sudo apt-get update
      sudo apt-get install build-essential

* On RHEL/Fedora:

  .. code-block:: bash

      sudo dnf groupinstall "Development Tools"

* Alternatively, when using conda, you can install the C++ compiler through conda:

  .. code-block:: bash

      conda install gxx_linux-64
