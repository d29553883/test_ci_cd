
FROM python:3.7
COPY . /
WORKDIR /
RUN mkdir system_log/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
ENV LISTEN_PORT=80
ENV DEBUG_MODE=False
ENV UseReloader=False
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
 