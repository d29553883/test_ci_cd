import uvicorn
import atexit
from fastapi import FastAPI, Request, Header, UploadFile, File
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from Controller.FirebaseController import *
from middleware import *
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import os, sys



# 取得環境辨識
ENV = os.getenv("ENV", "dev")
# 如果為正式環境，前面需要帶入 notify，組合就成為 /notify/api/v1.....
if ENV == "prod":
    prefix = "/notify"
else:
    prefix = ""

app = FastAPI(
    docs_url=prefix + "/api_docs",
    redoc_url=None,
    description="",
    openapi_url=prefix + "/openapi.json",
)


@app.get("/")
async def index():
    return {"message": "Access Denied"}


@app.post(prefix + "/v1/notifiaction/save")
def create_db(data: notify, request: Request):
    return FirebaseController.saveList(data)


# 測試自動發送email
@app.patch(prefix + "/v1/notifiaction/send_email")
def AutoSendEmail():
    return FirebaseController.auto_send_email()


# 測試自動發送sms
@app.get(prefix + "/v1/notifiaction/send_sms")
def AutoSendSms():
    return FirebaseController.auto_send_sms()


# 測試自動發送fcm
@app.get(prefix + "/v1/notifiaction/send_fcm")
def AutoSendFcm():
    return FirebaseController.auto_send_fcm()


# 測試立即發送sms
@app.post(prefix + "/v1/notifiaction/right_now_sms")
def RightNowSms(data: notify):
    return FirebaseController.right_now_sms(data)


# 測試立即發送email
@app.post(prefix + "/v1/notifiaction/right_now_email")
def RightNowEmail(data: notify):
    return FirebaseController.right_now_email(data)


# 測試存brand 資訊
@app.post(prefix + "/v1/notify_brand/save")
def create_db(data: brand):
    return FirebaseController.save_brand(data)


@app.get(prefix + "/v1/get_ip")
def get_ip():
    ip = requests.get("https://api.ipify.org").text
    return ip


@app.post(prefix + "/v1/send_email_with_products")
def send_email_with_products(data: dict):
    return FirebaseController.send_email_with_products(data)




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)
