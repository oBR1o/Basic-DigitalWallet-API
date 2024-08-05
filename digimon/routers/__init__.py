from . import router_items

def init_router(app):
    app.include_router(router_items.router)