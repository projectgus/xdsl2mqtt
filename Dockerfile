FROM python:3.11-alpine

WORKDIR /usr/src/app

RUN apk add --no-cache tzdata

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY xdsl2mqtt.py ./

CMD [ "./xdsl2mqtt.py", "-c", "/etc/xdsl2mqtt/config.ini" ]
