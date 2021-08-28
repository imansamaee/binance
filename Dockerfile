FROM python:3.6

ENV FLASK_APP run.py

COPY application.py gunicorn-cfg.py requirements.txt config.py .env ./
COPY application app

RUN pip install -r requirements.txt

EXPOSE 5005
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "run:app"]
