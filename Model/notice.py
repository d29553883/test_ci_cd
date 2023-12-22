from email.policy import default
from sqlalchemy import *
from database  import *
from sqlalchemy.orm import relationship, backref 
from sqlalchemy.types import UserDefinedType
import datetime
from datetime import timedelta,timezone
import decimal


class Notification(Base):
    __tablename__ = 'notification'
    id=Column('id',Integer, primary_key=True, autoincrement=True)
    brand_uuid=Column('brand_uuid',String(500))
    fcm_token=Column('fcm_token',String(500))
    type=Column('type',String(100))
    title=Column('title',String(200))
    body=Column('body',Text)
    image=Column('image',String(255))
    link=Column('link',String(255))
    arrival=Column('arrival',Integer)
    start_send_time=Column('start_send_time',Date)
    status=Column('status',Integer)
    created_at=Column('created_at',Date)
    updated_at=Column('updated_at',Date)
    
    
class Notify_email(Base):
    __tablename__ = 'notify_email'
    id=Column('id',Integer, primary_key=True, autoincrement=True)
    brand_uuid=Column('brand_uuid',String(500))
    to=Column('to',String(255))
    type=Column('type',String(100))
    title=Column('title',String(200))
    body=Column('body',Text)
    arrival=Column('arrival',Integer)
    start_send_time=Column('start_send_time',Date)
    status=Column('status',Integer)
    created_at=Column('created_at',Date)
    updated_at=Column('updated_at',Date)
    right_now=Column('right_now',Integer)

    

class Notify_sms(Base):
    __tablename__ = 'notify_sms'
    id=Column('id',Integer, primary_key=True, autoincrement=True)
    brand_uuid=Column('brand_uuid',String(500))
    to=Column('to',String(255))
    type=Column('type',String(100))
    body=Column('body',Text)
    arrival=Column('arrival',Integer)
    start_send_time=Column('start_send_time',Date)
    status=Column('status',Integer)
    created_at=Column('created_at',Date)
    updated_at=Column('updated_at',Date)
    right_now=Column('right_now',Integer)
    cost=Column('cost',Integer)
    
class Notify_brand(Base):
    __tablename__ = 'notify_brand'
    id=Column('id',Integer, primary_key=True, autoincrement=True)
    brand_code=Column('brand_code',String(100))
    brand_uuid=Column('brand_uuid',String(500))
    service_token=Column('service_token',String(500))
    brand_email=Column('brand_email',String(500))
    brand_phone=Column('brand_phone',String(100))