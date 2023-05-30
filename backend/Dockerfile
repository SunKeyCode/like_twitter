FROM python:3.10

COPY app /backend/app
COPY requirements.prod.txt requirements.txt

RUN pip install -r requirements.txt

COPY start_app.sh backend/start_app.sh

WORKDIR /backend/app/

RUN ["chmod", "+x", "../start_app.sh"]

CMD ["../start_app.sh"]