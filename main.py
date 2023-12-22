import uvicorn
from fastapi import FastAPI, Request, Header, UploadFile, File
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
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




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
