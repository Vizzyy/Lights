FROM python:3.8-slim
WORKDIR /usr/src/app
ENV TZ America/New_York
COPY . /usr/src/app
RUN pip install -r requirements.txt
CMD [ "python", "app.py" ]