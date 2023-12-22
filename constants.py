from datetime import datetime, timedelta
import os
import pytz


def get_prefix_time(data_dict):
    # 取得當前的時間
    today = datetime.today()

    # 取得台灣時區物件
    taiwan_tz = pytz.timezone("Asia/Taipei")

    # 將時間轉換為台灣時區
    today_taiwan = taiwan_tz.localize(today)
    yesterday = today_taiwan - timedelta(days=1)
    friday = today_taiwan - timedelta(days=3)
    month = yesterday.month
    day = yesterday.day
    friday_month = friday.month
    friady_day = friday.day

    weekday = today.weekday()
    WEEKDAY_NAME = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ][weekday]

    SEND_ENV = os.getenv("SEND_ENV")

    prefix = ""
    if SEND_ENV == "dev":
        prefix = "[dev]"
    if SEND_ENV == "test":
        prefix = "[test]"

    DEFAULT_SUBJECT = f"{prefix}{month}/{day}產品兌換單"

    MONDAY_SUBJECT = f"{prefix}{friday_month}/{friady_day} - {month}/{day}產品兌換單"

    if WEEKDAY_NAME == "Monday":
        data_dict["title"] = MONDAY_SUBJECT
    else:
        data_dict["title"] = DEFAULT_SUBJECT
    print(data_dict["title"])


DEFAULT_TEXT = "產品兌換單"


DEV_RECIPIENTS = ["davidlin@xaregroup.com"]
DEV_CC_RECIPIENTS = []

TEST_RECIPIENTS = ["davidlin@xaregroup.com", "wilsonchen@xaregroup.com"]
TEST_CC_RECIPIENTS = []

RECIPIENTS = ["kaylachiu@xaregroup.com", "shihengjian@xaregroup.com"]
CC_RECIPIENTS = [
    "davidlin@xaregroup.com",
    "wilsonchen@xaregroup.com",
    "edwardtseng@xaregroup.com",
]
