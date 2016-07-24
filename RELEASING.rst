Publishing
==========

::

    # Register with pypi (only done once)
    $ python setup.py register

    # Upload a new source distribution to PyPI
    $ python setup.py sdist upload

    # For each Python version, build and upload a binary distribution to PyPI
    $ source $PYTHON2_VENV/bin/activate && python setup.py bdist upload && deactivate
    $ source $PYTHON3_VENV/bin/activate && python setup.py bdist upload && deactivate
