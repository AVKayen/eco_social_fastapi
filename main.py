from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import encode, decode, exceptions
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "salty"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# TODO: Mati W, Change ID type to UUID
type Id = int

# User is the object passed around with JWT
class User(BaseModel):
    id: Id
    username: str

# UserFull is stored on the DB, extends User
class UserFull(User):
    password_hash: str
    streak: int = 0 # example, tbd
    # TODO: Mati W, Extend this User class to reflect the DB

    def to_user(self) -> User:
        return User(id=self.id, username=self.username)


class Token(BaseModel):
    access_token: str
    token_type: str


def generate_jwt_token(data: User, expires_delta: timedelta = None) -> Token:
    to_encode: dict = dict(data)
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return Token(
        access_token=encode(to_encode, SECRET_KEY, algorithm=ALGORITHM),
        token_type="bearer",
    )


class AuthService:
    def __init__(self):
        self.pass_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.users_db = {
            "tester": UserFull(id=1, username="tester", password_hash=self.pass_context.hash("password")),
        }

    def verify_password(self, plain_password, hashed_password):
        return self.pass_context.verify(plain_password, hashed_password)

    def authenticate_user(self, form: OAuth2PasswordRequestForm) -> User | None:
        # TODO: Modify below to reflect DB changes; pass password_hash from UserFull
        user_full: UserFull | None = self.users_db.get(form.username)
        if not user_full or not self.verify_password(form.password, user_full.password_hash):
            return None
        return user_full.to_user()


auth_service = AuthService()


def auth_get_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        payload.pop("exp", None)
        user = User(**payload)
        if user is None:
            raise exceptions.InvalidTokenError
        return user
    except exceptions.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth_service.authenticate_user(form_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return generate_jwt_token(user)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello")
async def say_hello(user: User = Depends(auth_get_user)):
    return {"message": f"Hello {user.username}"}

# TODO: User System
## Friend graph (adjacency network, relationships are two-way and must be accepted)


# TODO: Activity System (Addition, Editing, Types)
## User can create activities of certain type, description and photo
## Types:
## - bus_instead_of_car
## - ...
## Friends' activities in the Feed tab
## Each activity is attached to a pool of points that are added to the **Profile XP**
## At least one activity a day keeps **The Streak** alive
