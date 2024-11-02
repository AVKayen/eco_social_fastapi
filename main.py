from fastapi import Depends, FastAPI

# imports needed for the hello endpoint
from controller.auth_controller import parse_token, TokenData

from route.auth_router import auth_router
from route.user_router import user_router

app = FastAPI()


@app.get('/')
async def root():
    return {'message': 'Hello World'}


@app.get('/hello')
async def say_hello(token_data: TokenData = Depends(parse_token)):
    return {'message': f'Hello {token_data.username}'}


app.include_router(auth_router, prefix='/auth')
app.include_router(user_router, prefix='/user')

'''
TODO: User System
Friend graph (adjacency network, relationships are two-way and must be accepted)

TODO: Activity System (Addition, Editing, Types)
User can create activities of certain type, description and photo
Types:
- bus_instead_of_car
- ...
Friends activities in the Feed tab
Each activity is attached to a pool of points that are added to the **Profile XP**
At least one activity a day keeps **The Streak** alive
'''

