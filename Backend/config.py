from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    database_url: str = os.getenv("DATABASE_URL")

settings = Settings()