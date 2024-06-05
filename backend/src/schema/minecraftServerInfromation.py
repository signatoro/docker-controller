from typing import Any
from typing import Optional

import pytz

from pydantic import BaseModel

class McServerInformation(BaseModel):

    volumes: str
    
    max_ram: str | None = '2G'
    port: int | None = 25565
    rcon: str | None = 'super'
    hardcore: bool | None = False
    difficulty: int | None = 3
    version: str | None = 'latest'
    raw_timezone: str | None = 'America/New_York'
    reset_time: int | None = 3
    name: str | None = 'minecraft_server'
    seed: str | None = None
