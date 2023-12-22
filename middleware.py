from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional


class notify(BaseModel):
    brand_code: str
    brand_uuid: str
    fcm_token: Optional[str]
    service_token: Optional[str]
    title: Optional[str]
    to: Optional[str]
    type: str
    body: str
    image: Optional[str]
    link: Optional[str]
    domain: Optional[str]


class right_now_email(BaseModel):
    title: str
    to: str
    type: Optional[str]
    html: str


class brand(BaseModel):
    brand_code: str
    brand_uuid: str
    service_token: Optional[str]
    brand_email: Optional[str]
