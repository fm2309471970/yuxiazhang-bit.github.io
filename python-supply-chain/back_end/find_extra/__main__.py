import os
import sys

# Remove '' and current working directory from the first entry
# of sys.path, if present to avoid using current directory
# in find_extra commands check, freeze, install, list and show,
# when invoked as python -m find_extra <command>
if sys.path[0] in ("", os.getcwd()):
    sys.path.pop(0)

# If we are running from a wheel, add the wheel to sys.path
# This allows the usage python find_extra-*.whl/find_extra install find_extra-*.whl
if __package__ == "":
    # __file__ is find_extra-*.whl/find_extra/__main__.py
    # first dirname call strips of '/__main__.py', second strips off '/find_extra'
    # Resulting path is the name of the wheel itself
    # Add that to sys.path so we can import find_extra
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, path)

if __name__ == "__main__":
    from find_extra._internal.cli.main import main as _main

    sys.exit(_main())
