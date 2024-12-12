FROM python:3.13.1-alpine3.20
RUN nslookup pypi.org
COPY requirements.txt /
RUN pip3 install requests==2.32.3
RUN pip3 install -r /requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 5001
CMD [ "python3", "application.py" ]