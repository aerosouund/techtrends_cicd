FROM python:3.8


COPY . /app


WORKDIR /app


RUN pip install -r requirements.txt

# initialize db
RUN python init_db.py


EXPOSE 3111


CMD [ "python", "app.py" ]
