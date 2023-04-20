FROM python:3.10

COPY app /backend/app
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

WORKDIR /backend/app/

#CMD ["uvicorn", "--host=0.0.0.0", "main:app", "--reload"]
CMD ["python", "main.py"]