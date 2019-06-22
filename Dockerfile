FROM python:3.7
MAINTAINER Erokhin Dmitry <nefariusmag@gmail.com>
COPY requirements.txt .
RUN pip3 install -r ./requirements.txt
COPY alert.py .
ENTRYPOINT ["python", "alert.py"]
