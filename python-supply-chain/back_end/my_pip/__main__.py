import os
import sys

# Remove '' and current working directory from the first entry
# of sys.path, if present to avoid using current directory
# in my_pip commands check, freeze, install, list and show,
# when invoked as python -m my_pip <command>
if sys.path[0] in ("", os.getcwd()):
    sys.path.pop(0)

# If we are running from a wheel, add the wheel to sys.path
# This allows the usage python my_pip-*.whl/my_pip install my_pip-*.whl
if __package__ == "":
    # __file__ is my_pip-*.whl/my_pip/__main__.py
    # first dirname call strips of '/__main__.py', second strips off '/my_pip'
    # Resulting path is the name of the wheel itself
    # Add that to sys.path so we can import my_pip
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, path)

if __name__ == "__main__":
    from my_pip._internal.cli.main import main as _main

    sys.exit(_main())
