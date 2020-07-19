FROM python:3.6

WORKDIR /home/newuser/app

ADD . /home/newuser/app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["python", "main.py"]