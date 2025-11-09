# Bridge to existing src.app until full migration completed.
from importlib import import_module as _imp
try:
    _src_app = _imp('src.app')
    # re-export common names if defined
    if hasattr(_src_app, '__all__'):
        __all__ = _src_app.__all__  # type: ignore
except Exception:  # pragma: no cover
    __all__ = []
