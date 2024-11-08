from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
import os

# imports needed for the hello endpoint
from controller.auth_controller import parse_token, TokenData

from router.auth_router import auth_router
from router.user_router import user_router


UPLOAD_DIR = os.getenv('UPLOAD_DIR')
if not UPLOAD_DIR:
    raise Exception('No upload directory specified in the env variables')
os.makedirs(UPLOAD_DIR, exist_ok=True)


app = FastAPI()


@app.get('/')
async def root():
    return {'message': 'Hello World'}


@app.get('/hello')
async def say_hello(token_data: TokenData = Depends(parse_token)):
    return {'message': f'Hello {token_data.username}'}


app.mount('/static', StaticFiles(directory=UPLOAD_DIR), name='static')


app.include_router(auth_router)
app.include_router(user_router, prefix='/user')

'''
TODO: User System
- implement route for new friend recommendations

TODO: Activity System (Addition, Editing, Types)
User can create activities of certain type, description and photo
Types:
- bus_instead_of_car
- ...
Friends activities in the Feed tab
Each activity is attached to a pool of points that are added to the **Profile XP**
At least one activity a day keeps **The Streak** alive
'''
