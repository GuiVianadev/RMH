from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    database_url: str = os.getenv("DATABASE_URL")
    cloudinary_api_key: str = os.getenv("CLOUDNARY_API_KEY")
    cloudinary_api_secret: str = os.getenv("CLOUDNARY_API_SECRET")
    cloudinary_cloud_name: str = os.getenv("CLOUDNARY_CLOUD_NAME")

settings = Settings()