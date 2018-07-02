FROM python:3.5
MAINTAINER Erokhin Dmitry <derokhin@lanit.ru>
USER root
# закидываю файлы для работы
COPY *.py /opt/
COPY *.txt /opt/
RUN mkdir /opt/deploy_sti && mkdir /opt/error_sti && mkdir /opt/kill_sti && mkdir /opt/logs_sti && mkdir /opt/true_sti
COPY deploy_sti/* /opt/deploy_sti/
COPY error_sti/* /opt/error_sti/
COPY kill_sti/* /opt/kill_sti/
COPY logs_sti/* /opt/logs_sti/
COPY true_sti/* /opt/true_sti/
# установка нужных программ для работы
RUN pip3 install -r /opt/requirements.txt
WORKDIR /opt
ENTRYPOINT ["python", "telegram_jenkins.py"]
