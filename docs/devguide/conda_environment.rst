********************************************************************************
Development Environment
********************************************************************************

The canonical development environment is managed by uv and recorded in
``uv.lock``.

Install the development dependency group
----------------------------------------

.. code-block:: bash

    uv sync --frozen --group dev

Run tools without activating the environment
--------------------------------------------

.. code-block:: bash

    uv run pytest
    uv run ruff check .
    uv run ruff format --check .
    uv run pyright

The ``dev``, ``docs``, and ``viz`` dependency groups in ``pyproject.toml``
replace the former Conda and requirements manifests. Until COMPAS 3 is
published, the lock uses the exact coordinated COMPAS Git candidate recorded
in ``[tool.uv.sources]``.
