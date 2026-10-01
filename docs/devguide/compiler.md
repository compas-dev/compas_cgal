# Compiler Requirements

Before installing COMPAS CGAL, you need to ensure you have the
appropriate C++ compiler setup for your operating system:

## Windows

- Install Visual Studio Build Tools (2022 or newer)
- During installation, select "Desktop development with C++"
- No additional PATH settings are required as CMake will automatically
  find the compiler

## macOS

- Install Xcode Command Line Tools:

  ``` bash
  xcode-select --install
  ```

- The clang compiler will be automatically available after installation

## Linux

- Install GCC and related build tools. On Ubuntu/Debian:

  ``` bash
  sudo apt-get update
  sudo apt-get install build-essential
  ```

- On RHEL/Fedora:

  ``` bash
  sudo dnf groupinstall "Development Tools"
  ```

- Alternatively, when using conda, you can install the C++ compiler
  through conda:

  ``` bash
  conda install gxx_linux-64
  ```
