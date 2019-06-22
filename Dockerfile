FROM python:3.7
MAINTAINER Erokhin Dmitry <nefariusmag@gmail.com>
COPY alert.py .
COPY requirements.txt .
RUN pip3 install -r ./requirements.txt
ENTRYPOINT ["python", "alert.py"]
