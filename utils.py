import os
import requests
import collections
from phpserialize import unserialize
from fastapi.responses import StreamingResponse
from io import StringIO
import csv
import io
import datetime


def Dict2Ary(self, data):
    setData = collections.OrderedDict()
    if isinstance(data, dict):
        for k, v in data.items():
            setData[k] = v
    else:
        for key, value in data:
            setData[key] = value
    return setData


def csv_download(prize_sql, headers, filename):
    loc_dt = datetime.datetime.today()
    today = loc_dt.strftime("%Y/%m/%d")
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(headers)
    for i in prize_sql:
        cw.writerow(list(i))
    output = StreamingResponse(
        iter([si.getvalue().encode("utf-8-sig")]), media_type="text/csv"
    )
    output.headers["Content-Disposition"] = "attachment; filename=" + filename
    output.headers["Content-type"] = "text/csv"

    return output
