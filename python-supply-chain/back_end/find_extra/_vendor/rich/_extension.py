from typing import Any


def load_ipython_extension(ip: Any) -> None:  # pragma: no cover
    # prevent circular import
    from find_extra._vendor.rich.pretty import install
    from find_extra._vendor.rich.traceback import install as tr_install

    install()
    tr_install()
