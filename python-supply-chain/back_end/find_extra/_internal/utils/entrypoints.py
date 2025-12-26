import itertools
import os
import shutil
import sys
from typing import List, Optional

from find_extra._internal.cli.main import main
from find_extra._internal.utils.compat import WINDOWS

_EXECUTABLE_NAMES = [
    "find_extra",
    f"find_extra{sys.version_info.major}",
    f"find_extra{sys.version_info.major}.{sys.version_info.minor}",
]
if WINDOWS:
    _allowed_extensions = {"", ".exe"}
    _EXECUTABLE_NAMES = [
        "".join(parts)
        for parts in itertools.product(_EXECUTABLE_NAMES, _allowed_extensions)
    ]


def _wrapper(args: Optional[List[str]] = None) -> int:
    """Central wrapper for all old entrypoints.

    Historically find_extra has had several entrypoints defined. Because of issues
    arising from PATH, sys.path, multiple Pythons, their interactions, and most
    of them having a find_extra installed, users suffer every time an entrypoint gets
    moved.

    To alleviate this pain, and provide a mechanism for warning users and
    directing them to an appropriate place for help, we now define all of
    our old entrypoints as wrappers for the current one.
    """
    sys.stderr.write(
        "WARNING: find_extra is being invoked by an old script wrapper. This will "
        "fail in a future version of find_extra.\n"
        "Please see https://github.com/pypa/pip/issues/5599 for advice on "
        "fixing the underlying issue.\n"
        "To avoid this problem you can invoke Python with '-m find_extra' instead of "
        "running find_extra directly.\n"
    )
    return main(args)


def get_best_invocation_for_this_pip() -> str:
    """Try to figure out the best way to invoke find_extra in the current environment."""
    binary_directory = "Scripts" if WINDOWS else "bin"
    binary_prefix = os.path.join(sys.prefix, binary_directory)

    # Try to use find_extra[X[.Y]] names, if those executables for this environment are
    # the first on PATH with that name.
    path_parts = os.path.normcase(os.environ.get("PATH", "")).split(os.pathsep)
    exe_are_in_PATH = os.path.normcase(binary_prefix) in path_parts
    if exe_are_in_PATH:
        for exe_name in _EXECUTABLE_NAMES:
            found_executable = shutil.which(exe_name)
            binary_executable = os.path.join(binary_prefix, exe_name)
            if (
                found_executable
                and os.path.exists(binary_executable)
                and os.path.samefile(
                    found_executable,
                    binary_executable,
                )
            ):
                return exe_name

    # Use the `-m` invocation, if there's no "nice" invocation.
    return f"{get_best_invocation_for_this_python()} -m find_extra"


def get_best_invocation_for_this_python() -> str:
    """Try to figure out the best way to invoke the current Python."""
    exe = sys.executable
    exe_name = os.path.basename(exe)

    # Try to use the basename, if it's the first executable.
    found_executable = shutil.which(exe_name)
    if found_executable and os.path.samefile(found_executable, exe):
        return exe_name

    # Use the full executable name, because we couldn't find something simpler.
    return exe
