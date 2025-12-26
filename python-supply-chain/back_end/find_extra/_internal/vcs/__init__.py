# Expose a limited set of classes and functions so callers outside of
# the vcs package don't need to import deeper than `find_extra._internal.vcs`.
# (The test directory may still need to import from a vcs sub-package.)
# Import all vcs modules to register each VCS in the VcsSupport object.
import find_extra._internal.vcs.bazaar
import find_extra._internal.vcs.git
import find_extra._internal.vcs.mercurial
import find_extra._internal.vcs.subversion  # noqa: F401
from find_extra._internal.vcs.versioncontrol import (  # noqa: F401
    RemoteNotFoundError,
    RemoteNotValidError,
    is_url,
    make_vcs_requirement_url,
    vcs,
)
