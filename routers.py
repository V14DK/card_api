from typing import List
from fastapi import FastAPI
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse
from core.schemas.schema import User, Event
from core.models.database import get_session
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from core.events.service import add_event, read_events
from core.auth.service import validate_create_user, user_login, get_user_profile, remove_token


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
router = APIRouter()


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    auth = user_login(form_data, session)
    auth.update({"message": "Successful login"})
    return JSONResponse(content=auth)


@router.post("/register")
async def register(form_data: User, session: Session = Depends(get_session)) -> object:
    auth = validate_create_user(form_data, session)
    auth.update({"message": "User is created"})
    return JSONResponse(content=auth)


@router.get("/logout")
async def logout(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    return remove_token(token, session)


@router.get("/profile", response_model=User)
async def get_profile(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    return get_user_profile(token, session)


@router.post('/events/create')
async def create_event(event: Event, token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    return add_event(user=token, session=session, event=event)


@router.get('/events', response_model=List[Event])
async def get_events(session: Session = Depends(get_session)):
    return read_events(session)

app.include_router(router)
