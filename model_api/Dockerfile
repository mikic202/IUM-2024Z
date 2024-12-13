FROM pytorch/pytorch:latest
# RUN nslookup pypi.org
# RUN pip install torch-geometric torchvision scikit-learn
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 5000
CMD [ "python3", "application.py" ]