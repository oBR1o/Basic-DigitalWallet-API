from . import items, merchants

def init_router(app):
    app.include_router(items.router)
    app.inclide_router(merchants.router)