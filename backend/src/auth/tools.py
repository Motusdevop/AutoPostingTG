from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from settings import Settings, get_settings

cfg: Settings = get_settings()

security = HTTPBasic()


def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    username = get_username()
    password = get_password()
    if username != credentials.username and password != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    return True


def get_password():
    return cfg.password


def get_username():
    return cfg.username
