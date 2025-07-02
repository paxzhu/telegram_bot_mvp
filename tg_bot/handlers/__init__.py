from .intro_flow import router as intro_router
from .memory import router as memory_router
from .recent import router as recent_router
from .start import router as start_router

all_routers = [intro_router, memory_router, recent_router, start_router]