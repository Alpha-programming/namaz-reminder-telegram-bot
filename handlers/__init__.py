from .commands import router as commands_router
from .texts import router as texts_router
from .callbacks import router as callbacks_router

routers_list = [
    commands_router,
    texts_router,
    callbacks_router
]