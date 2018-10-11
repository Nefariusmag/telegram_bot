FROM python:3.6
MAINTAINER Erokhin Dmitry <derokhin@lanit.ru>
USER root
COPY requirements.txt /opt/
# установка нужных программ для работы
RUN pip3 install -r /opt/requirements.txt
# закидываю файлы для работы
COPY *.py /opt/
WORKDIR /opt
ENTRYPOINT ["python", "main.py"]
