from fastapi import FastAPI

# Documentation
from documentation.description import api_description
from documentation.tags import tags_metadata

#import router
import routers.router_auth
import routers.router_meetingRoom
import routers.router_strip

app = FastAPI(
    title="bookingRoom",
    description=api_description, 
    openapi_tags=tags_metadata
)

app.include_router(routers.router_auth.router)
app.include_router(routers.router_meetingRoom.router)
app.include_router(routers.router_strip.router)

