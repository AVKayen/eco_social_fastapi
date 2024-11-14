from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
import os

# imports needed for the hello endpoint
from controller.auth_controller import parse_token, TokenData

from router.auth_router import auth_router
from router.user_router import user_router
from router.activity_router import activity_router

from config.settings import settings


os.makedirs(settings.upload_dir, exist_ok=True)


app = FastAPI()

origins = [
    "http://localhost:40191",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def update_response_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers['Charset'] = 'utf-8'
    return response

@app.get('/')
async def root():
    return {'message': 'Hello World'}


@app.get('/hello')
async def say_hello(token_data: TokenData = Depends(parse_token)):
    return {'message': f'Hello {token_data.username}'}


app.mount('/static', StaticFiles(directory=settings.upload_dir), name='static')


app.include_router(auth_router)
app.include_router(user_router, prefix='/user')
app.include_router(activity_router, prefix='/activity')

'''
TODO: User System


TODO: Activity System (Addition, Editing, Types)
User can create activities of certain type, description and photo
Types:
- bus_instead_of_car
- ...
Make only a portion of feed load
Each activity is attached to a pool of points that are added to the **Profile XP**
At least one activity a day keeps **The Streak** alive
'''
