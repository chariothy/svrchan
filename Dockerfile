# For githook project
# @version 1.0

FROM python:3.8
LABEL maintainer="chariothy@gmail.com"

EXPOSE 8822

ENV HOST=0.0.0.0

ENV SVRCHAN_MAIL_FROM="Henry TIAN <chariothy@gmail.com>"
ENV SVRCHAN_MAIL_TO="Henry TIAN <chariothy@gmail.com>"

ENV SVRCHAN_SMTP_HOST=smtp.gmail.com
ENV SVRCHAN_SMTP_PORT=25
ENV SVRCHAN_SMTP_USER=chariothy@gmail.com
ENV SVRCHAN_SMTP_PWD=password

ENV SVRCHAN_NOTIFY_MAIL=1
ENV SVRCHAN_NOTIFY_DINGTALK=0

ENV SVRCHAN_DINGTALK_TOKEN=DINGTALK_BOT_TOKEN
ENV SVRCHAN_DINGTALK_SECRET=DINGTALK_BOT_SECRET

ENV SVRCHAN_RELOAD=0

COPY ./requirements.txt .

RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
  && echo 'Asia/Shanghai' > /etc/timezone \
  && pip install -U pip \
  && pip install --no-cache-dir -r ./requirements.txt
  
WORKDIR /app/svrchan

CMD [ "python", "server.py" ]