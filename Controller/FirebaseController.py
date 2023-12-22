from Model.notice import *
import os
import json
import csv
import collections
import pytz
import requests, pickle
from datetime import datetime, timedelta
from multiprocessing.dummy import Pool as ThreadPool


EVENT_ENDPOINT = os.getenv("EVENT_ENDPOINT")
mg_key = os.getenv("MG_API_KEY")
sms_username = os.getenv("MITAKE_USERNAME")
sms_password = os.getenv("MITAKE_PASSWORD")


class FirebaseController:
    # 存入推播名單
    def saveList(data):
        if data is None:
            return {"code": -2, "reason": "沒有帶入資料"}, 400
        if "start_send_time" not in data:
            start_send_time = (datetime.utcnow() + timedelta(hours=8)).isoformat()
        else:
            start_send_time = data["start_send_time"]

        insert_fcm = Notification(
            brand_uuid=data.brand_uuid,
            fcm_token=data.fcm_token,
            type=data.type,
            title=data.title,
            body=data.body,
            image=data.image,
            link=data.link,
            arrival=0,
            start_send_time=start_send_time,
            status=0,
            created_at=(datetime.utcnow() + timedelta(hours=8)).isoformat(),
            updated_at=(datetime.utcnow() + timedelta(hours=8)).isoformat(),
        )
        insert_email = Notify_email(
            brand_uuid=data.brand_uuid,
            to=data.to,
            type=data.type,
            title=data.title,
            body=data.body,
            arrival=0,
            start_send_time=start_send_time,
            status=0,
            created_at=(datetime.utcnow() + timedelta(hours=8)).isoformat(),
            updated_at=(datetime.utcnow() + timedelta(hours=8)).isoformat(),
        )
        insert_sms = Notify_sms(
            brand_uuid=data.brand_uuid,
            to=data.to,
            type=data.type,
            body=data.body,
            arrival=0,
            start_send_time=start_send_time,
            status=0,
            created_at=(datetime.utcnow() + timedelta(hours=8)).isoformat(),
            updated_at=(datetime.utcnow() + timedelta(hours=8)).isoformat(),
        )
        session_save = SWrite()
        try:
            if data.type == "fcm":
                session_save.add(insert_fcm)
                session_save.commit()
                session_save.close()
                return {"status": "success"}, 200
            if data.type == "email":
                session_save.add(insert_email)
                session_save.commit()
                session_save.close()
                return {"status": "success"}, 200
            if data.type == "sms":
                session_save.add(insert_sms)
                session_save.commit()
                session_save.close()
                return {"status": "success"}, 200
        except Exception as e:
            session_save.rollback()
            session_save.close()
            return {"code": -10, "reason": "發生異常錯誤", "msg": str(e)}, 500

    def auto_send_email():
        session_email = SRead()
        sql = "select notify_email.id, notify_email.brand_uuid, notify_email.to, notify_email.type, notify_email.title, notify_email.body, notify_brand.brand_email, notify_brand.brand_uuid, notify_brand.service_token from notify_email join notify_brand on notify_email.brand_uuid = notify_brand.brand_uuid where notify_email.arrival = 0 order by notify_email.id limit 200"

        rows = session_email.execute(sql)
        print(rows)
        session_email.close()
        list_of_args = []
        ids = []
        for i in rows:
            list_of_args.append(
                {
                    "id": i.id,
                    "from": i.brand_email,
                    "to": i.to,
                    "title": i.title,
                    "body": i.body,
                }
            )
            ids.append(i.id)
        del rows
        if len(list_of_args) == 0:
            return {"code": -1, "reason": "沒有要發送的資料"}, 404

        session_email_update = SWrite()
        session_email_update.query(Notify_email).filter(
            Notify_email.id.in_(ids)
        ).update({Notify_email.arrival: 3}, synchronize_session="fetch")
        session_email_update.commit()
        session_email_update.close()

        pool = ThreadPool(1)
        re = pool.map(send_email_message, list_of_args)
        pool.close()
        pool.join()
        session_refcm = SWrite()
        for r in re:
            if r["status"] == "Success":
                session_refcm.query(Notify_email).filter(
                    Notify_email.id == r["notify_email_id"]
                ).update(
                    {
                        Notify_email.arrival: 1,
                        Notify_email.updated_at: (
                            datetime.utcnow() + timedelta(hours=8)
                        ).isoformat(),
                    }
                )
            else:
                session_refcm.query(Notify_email).filter(
                    Notify_email.id == r["notify_email_id"]
                ).update(
                    {
                        Notify_email.arrival: 2,
                        Notify_email.updated_at: (
                            datetime.utcnow() + timedelta(hours=8)
                        ).isoformat(),
                    }
                )

        session_refcm.commit()
        session_refcm.close()
        return {"code": 1, "reason": "發送完成"}, 200

    def right_now_sms(data):
        try:
            print(data)
            if data is None:
                return {"code": -2, "reason": "沒有帶入資料"}, 400
            if "start_send_time" not in data:
                start_send_time = (datetime.utcnow() + timedelta(hours=8)).isoformat()
            else:
                start_send_time = data["start_send_time"]
            insert_sms = Notify_sms(
                brand_uuid=data.brand_uuid,
                to=data.to,
                type=data.type,
                body=data.body,
                arrival=0,
                start_send_time=start_send_time,
                status=0,
                right_now=1,
                created_at=(datetime.utcnow() + timedelta(hours=8)).isoformat(),
                updated_at=(datetime.utcnow() + timedelta(hours=8)).isoformat(),
            )
            session_save = SWrite()
            session_save.add(insert_sms)
            session_save.commit()
            session_save.close()

            session_sms = SRead()
            sql = "select notify_sms.id, notify_sms.brand_uuid, notify_sms.to, notify_sms.type, notify_sms.body, notify_brand.brand_uuid, notify_brand.brand_phone from notify_sms join notify_brand on notify_sms.brand_uuid = notify_brand.brand_uuid where notify_sms.arrival = 0 and notify_sms.right_now = 1 order by notify_sms.id limit 2"
            rows = session_sms.execute(sql)
            session_sms.close()
            list_of_args = []
            ids = []
            for i in rows:
                list_of_args.append(
                    {"id": i.id, "from": i.brand_phone, "to": i.to, "body": i.body}
                )
                ids.append(i.id)
            del rows
            if len(list_of_args) == 0:
                return {"code": -1, "reason": "沒有要發送的資料"}, 404

            session_sms_update = SWrite()
            session_sms_update.query(Notify_sms).filter(Notify_sms.id.in_(ids)).update(
                {Notify_sms.arrival: 3}, synchronize_session="fetch"
            )
            session_sms_update.commit()
            session_sms_update.close()
            pool = ThreadPool(1)
            re = pool.map(send_sms_message, list_of_args)
            pool.close()
            pool.join()
            session_resms = SWrite()

            for r in re:
                if r["status"] == "Success":
                    cost = r["cost"]
                    session_resms.query(Notify_sms).filter(
                        Notify_sms.id == r["notify_sms_id"]
                    ).update(
                        {
                            Notify_sms.arrival: 1,
                            Notify_sms.updated_at: (
                                datetime.utcnow() + timedelta(hours=8)
                            ).isoformat(),
                            Notify_sms.cost: cost,
                        }
                    )
                else:
                    session_resms.query(Notify_sms).filter(
                        Notify_sms.id == r["notify_sms_id"]
                    ).update(
                        {
                            Notify_sms.arrival: 2,
                            Notify_sms.updated_at: (
                                datetime.utcnow() + timedelta(hours=8)
                            ).isoformat(),
                        }
                    )

            session_resms.commit()
            session_resms.close()
            return {"code": 1, "reason": "發送完成"}, 200
        except Exception as error:
            return {"code": 500, "message": str(error)}

    def right_now_email(data):
        if data is None:
            return {"code": -2, "reason": "沒有帶入資料"}, 400
        if "start_send_time" not in data:
            start_send_time = (datetime.utcnow() + timedelta(hours=8)).isoformat()
        else:
            start_send_time = data["start_send_time"]
        insert_email = Notify_email(
            brand_uuid=data.brand_uuid,
            to=data.to,
            type=data.type,
            title=data.title,
            body=data.body,
            arrival=0,
            start_send_time=start_send_time,
            status=0,
            right_now=1,
            created_at=(datetime.utcnow() + timedelta(hours=8)).isoformat(),
            updated_at=(datetime.utcnow() + timedelta(hours=8)).isoformat(),
        )
        session_save = SWrite()
        session_save.add(insert_email)
        session_save.commit()
        session_save.close()

        session_email = SRead()
        sql = "select notify_email.id, notify_email.brand_uuid, notify_email.to, notify_email.type, notify_email.title, notify_email.body, notify_brand.brand_email, notify_brand.brand_uuid, notify_brand.service_token from notify_email join notify_brand on notify_email.brand_uuid = notify_brand.brand_uuid where notify_email.arrival = 0 and notify_email.right_now = 1  order by notify_email.id limit 5"
        rows = session_email.execute(sql)
        session_email.close()
        list_of_args = []
        ids = []

        for i in rows:
            brand_email = "xare享生活客服信箱" + "<" + i.brand_email + ">"
            list_of_args.append(
                {
                    "id": i.id,
                    "from": brand_email,
                    "to": i.to,
                    "title": i.title,
                    "body": i.body,
                }
            )
            ids.append(i.id)
        del rows
        if len(list_of_args) == 0:
            return {"code": -1, "reason": "沒有要發送的資料"}, 404
        session_email_update = SWrite()
        session_email_update.query(Notify_email).filter(
            Notify_email.id.in_(ids)
        ).update({Notify_email.arrival: 3}, synchronize_session="fetch")
        session_email_update.commit()
        session_email_update.close()
        pool = ThreadPool(1)
        re = pool.map(send_email_message, list_of_args)
        pool.close()
        pool.join()
        session_email = SWrite()
        for r in re:
            if r["status"] == "Success":
                session_email.query(Notify_email).filter(
                    Notify_email.id == r["notify_email_id"]
                ).update(
                    {
                        Notify_email.arrival: 1,
                        Notify_email.updated_at: (
                            datetime.utcnow() + timedelta(hours=8)
                        ).isoformat(),
                    }
                )
            else:
                session_email.query(Notify_email).filter(
                    Notify_email.id == r["notify_email_id"]
                ).update(
                    {
                        Notify_email.arrival: 2,
                        Notify_email.updated_at: (
                            datetime.utcnow() + timedelta(hours=8)
                        ).isoformat(),
                    }
                )

        session_email.commit()
        session_email.close()
        return {"code": 1, "reason": "發送完成"}, 200

    def auto_send_sms():
        session_sms = SRead()
        sql = "select notify_sms.id, notify_sms.brand_uuid, notify_sms.to, notify_sms.type, notify_sms.body, notify_brand.brand_uuid, notify_brand.brand_phone from notify_sms join notify_brand on notify_sms.brand_uuid = notify_brand.brand_uuid where notify_sms.arrival = 0 order by notify_sms.id limit 200"
        rows = session_sms.execute(sql)
        session_sms.close()
        list_of_args = []
        ids = []
        for i in rows:
            list_of_args.append(
                {"id": i.id, "from": i.brand_phone, "to": i.to, "body": i.body}
            )
            ids.append(i.id)
        del rows
        if len(list_of_args) == 0:
            return {"code": -1, "reason": "沒有要發送的資料"}, 404

        session_sms_update = SWrite()
        session_sms_update.query(Notify_sms).filter(Notify_sms.id.in_(ids)).update(
            {Notify_sms.arrival: 3}, synchronize_session="fetch"
        )
        session_sms_update.commit()
        session_sms_update.close()
        pool = ThreadPool(1)
        re = pool.map(send_sms_message, list_of_args)
        pool.close()
        pool.join()
        session_resms = SWrite()
        for r in re:
            if r["status"] == "Success":
                cost = r["cost"]
                session_resms.query(Notify_sms).filter(
                    Notify_sms.id == r["notify_sms_id"]
                ).update(
                    {
                        Notify_sms.arrival: 1,
                        Notify_sms.updated_at: (
                            datetime.utcnow() + timedelta(hours=8)
                        ).isoformat(),
                        Notify_sms.cost: cost,
                    }
                )
            else:
                session_resms.query(Notify_sms).filter(
                    Notify_sms.id == r["notify_sms_id"]
                ).update(
                    {
                        Notify_sms.arrival: 2,
                        Notify_sms.updated_at: (
                            datetime.utcnow() + timedelta(hours=8)
                        ).isoformat(),
                    }
                )

        session_resms.commit()
        session_resms.close()
        return {"code": 1, "reason": "發送完成"}, 200

    def auto_send_fcm():
        session_fcm = SRead()
        sql = "select notification.id, notification.brand_uuid, notification.fcm_token, notification.type, notification.title, notification.body, notification.image, notify_brand.brand_uuid, notify_brand.service_token, notify_brand.brand_email from notification join notify_brand on notification.brand_uuid = notify_brand.brand_uuid where notification.arrival = 0 order by notification.id limit 200"
        rows = session_fcm.execute(sql)
        session_fcm.close()
        list_of_args = []
        ids = []
        for i in rows:
            list_of_args.append(
                {
                    "id": i.id,
                    "service_token": i.service_token,
                    "to": i.fcm_token,
                    "title": i.title,
                    "body": i.body,
                    "image": i.image,
                }
            )
            ids.append(i.id)
        del rows
        if len(list_of_args) == 0:
            return {"code": -1, "reason": "沒有要發送的資料"}, 404

        session_fcm_update = SWrite()
        session_fcm_update.query(Notification).filter(Notification.id.in_(ids)).update(
            {Notification.arrival: 3}, synchronize_session="fetch"
        )
        session_fcm_update.commit()
        session_fcm_update.close()
        pool = ThreadPool(1)
        re = pool.map(sendFCM, list_of_args)
        pool.close()
        pool.join()
        session_refcm = SWrite()
        for r in re:
            if r["status"] == "Success":
                session_refcm.query(Notification).filter(
                    Notification.id == r["notify_id"]
                ).update(
                    {
                        Notification.arrival: 1,
                        Notification.updated_at: (
                            datetime.utcnow() + timedelta(hours=8)
                        ).isoformat(),
                    }
                )
            else:
                session_refcm.query(Notification).filter(
                    Notification.id == r["notify_id"]
                ).update(
                    {
                        Notification.arrival: 2,
                        Notification.updated_at: (
                            datetime.utcnow() + timedelta(hours=8)
                        ).isoformat(),
                    }
                )

        session_refcm.commit()
        session_refcm.close()
        return {"code": 1, "reason": "發送完成"}, 200

    def save_brand(data):
        insert_brand = Notify_brand(
            brand_code=data.brand_code,
            brand_uuid=data.brand_uuid,
            service_token=data.service_token,
            brand_email=data.brand_email,
        )
        try:
            session_save = SWrite()
            session_save.add(insert_brand)
            session_save.commit()
            session_save.close()
            return {"status": "success"}, 200

        except Exception as e:
            session_save.rollback()
            session_save.close()
            return {"code": -10, "reason": "發生異常錯誤", "msg": str(e)}, 500

    def send_email_with_products(payload):
        try:
            today = datetime.today()
            taiwan_tz = pytz.timezone("Asia/Taipei")
            today_taiwan = taiwan_tz.localize(today)
            yesterday = today_taiwan - timedelta(days=1)
            friday = today_taiwan - timedelta(days=3)
            weekday = today_taiwan.weekday()
            WEEKDAY_NAME = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ][weekday]
            print(WEEKDAY_NAME)
            if WEEKDAY_NAME != "Saturday" and WEEKDAY_NAME != "Sunday":
                start_date = datetime(
                    yesterday.year, yesterday.month, yesterday.day, 0, 0, 0
                )
                end_date = datetime(today.year, today.month, today.day, 0, 0, 0)
                if WEEKDAY_NAME == "Monday":
                    start_date = datetime(
                        friday.year, friday.month, friday.day, 0, 0, 0
                    )
                r = requests.get(
                    f"{EVENT_ENDPOINT}/event/v1/report/products?start_date={start_date}&end_date={end_date}",
                )
                r = r.json()
                # 寫入 CSV 數據到臨時文件
                with open(
                    "./products_exchanges_list.csv",
                    "w",
                    newline="",
                    encoding="utf-8-sig",
                ) as file:
                    writer = csv.writer(file)
                    writer.writerow(r["headers"])
                    for i in r["data"]:
                        datetime_obj = datetime.strptime(i["購買日期"], "%Y-%m-%dT%H:%M:%S")
                        i["購買日期"] = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
                        i["電話"] = "=" + '"' + i["電話"] + '"'
                        i["訂單流水號"] = "=" + '"' + str(i["訂單流水號"]) + '"'
                        writer.writerow(i.values())
                url = "https://api.mailgun.net/v3/mg.xaregroup.com/messages"
                auth = ("api", mg_key)

                with open("./products_exchanges_list.csv", "rb") as file:
                    attachment_data = file.read()

                data = {
                    "from": "xare享生活客服信箱" + "<" + "cs@xaregroup.com" + ">",
                    "to": payload["to"],
                    "cc": payload["cc"],
                    "subject": payload["title"],
                    "text": payload["text"],
                }
                files = [
                    (
                        "attachment",
                        (
                            "./products_exchanges_list.csv",
                            attachment_data,
                            "application/csv",
                        ),
                    )
                ]
                response = requests.post(url, auth=auth, data=data, files=files)
                if response.status_code == 200:
                    print("Email sent successfully.")
                    return {"status": "success", "data": []}, 200
                else:
                    print("Failed to send email. Status code:", response.status_code)
                    return {"status": "fail"}, 500
        except Exception as error:
            return {"code": 500, "message": str(error)}


def sendFCM(args):
    try:
        deviceToken = args["to"]
        serverToken = args["service_token"]
        headers = {
            "Content-Type": "application/json",
            "Authorization": "key=" + serverToken,
        }
        body = {
            "notification": {
                "title": args["title"],
                "body": args["body"],
                "image": args["image"],
            },
            "to": deviceToken,
            "priority": "high",
            "content_available": True,
            "mutable-content": 1,
        }
        print(headers)
        print(body)
        response = requests.post(
            "https://fcm.googleapis.com/fcm/send",
            headers=headers,
            data=json.dumps(body),
        )
        if response.status_code == 200:
            return {"notify_id": args["id"], "status": "Success"}
        else:
            return {"notify_id": args["id"], "status": "Fail"}

    except Exception as error:
        return {"notify_id": args["id"], "status": "Fail", "reason": str(error)}


def send_email_message(args):
    response = requests.post(
        "https://api.mailgun.net/v3/mg.xaregroup.com/messages",
        auth=("api", mg_key),
        data={
            "from": args["from"],
            "to": args["to"],
            "subject": args["title"],
            "html": args["body"],
        },
    )

    if response.status_code == 200:
        return {"notify_email_id": args["id"], "status": "Success"}
    else:
        return {"notify_email_id": args["id"], "status": "Fail"}


def send_sms_message(args):
    try:
        result = requests.post(
            "https://smsapi.mitake.com.tw/api/mtk/SmQuery",
            data={"username": sms_username, "password": sms_password},
        )
        print(result.text)
        # 當前剩餘點數
        AccountPoint = int(result.text[13:])

        dstaddr = args["to"]
        sms_body = args["body"]
        response = requests.get(
            "https://smsapi.mitake.com.tw/api/mtk/SmSend?"
            + "username="
            + sms_username
            + "&password="
            + sms_password
            + "&dstaddr="
            + dstaddr
            + "&smbody="
            + sms_body
            + "&CharsetURL=UTF-8"
        )
        response = response.text
        print(response)
        AfterPoint = ""
        word = response.split("\r\n")
        for i in word:
            x = i.split("=")
            if x[0] == "Error":
                return {"notify_sms_id": args["id"], "status": "Fail"}
            if x[0] == "AccountPoint":
                AfterPoint = int(x[1])
        cost = AccountPoint - AfterPoint

        return {"notify_sms_id": args["id"], "status": "Success", "cost": cost}
    except Exception as error:
        return {"code": 500, "message": str(error)}
