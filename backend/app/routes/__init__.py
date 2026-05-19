"""Package initializer for app.routes.

Expose route submodules so `from app.routes import nasa` works reliably.
"""
from . import nasa, products, user

__all__ = ["nasa", "products", "user"]
