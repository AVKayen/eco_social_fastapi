from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


# TODO: User System
## Friend graph (adjacency network, relationships are two-way and must be accepted)
##JWT Auth (skipped for prototype, authentication is implicit)


# TODO: Activity System (Addition, Editing, Types)
## User can create activities of certain type, description and photo
## Types:
## - bus_instead_of_car
## - ...
## Friends' activities in the Feed tab
## Each activity is attached to a pool of points that are added to the **Profile XP**
## At least one activity a day keeps **The Streak** alive
