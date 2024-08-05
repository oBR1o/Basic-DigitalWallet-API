from . import items

def init_router(app):
    app.include_router(items.router)