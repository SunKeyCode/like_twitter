FROM python:3.10

COPY app /backend/app
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY start_app.sh backend/start_app.sh

WORKDIR /backend/app/

RUN ["chmod", "+x", "../start_app.sh"]

#ENV DEBUG=true

CMD ["../start_app.sh"]