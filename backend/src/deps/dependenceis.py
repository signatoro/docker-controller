

import os
import bcrypt

from enum import Enum
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends

load_dotenv()



class DiscordRoute(APIRouter):
    def __init__(self, tags: list[str | Enum] | None = None, prefix: str = "", **kwargs):
        super().__init__(tags=tags, prefix=prefix, dependencies=[Depends(verify_requestion)], **kwargs)


async def verify_requestion(token: str):
    print(os.getenv("PUBLIC_TOKEN"))
    print(hash_token(token).encode('utf-8'))
    if bcrypt.checkpw(hash_token(token).encode('utf-8'), os.getenv("PUBLIC_TOKEN").encode('utf-8')):
        raise HTTPException(401, 'Access Denied')
    
def hash_token(token: str) -> bytes:
    """Hash a password for the first time, with a randomly-generated salt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(token.encode('utf-8'), salt)
    return hashed.decode()