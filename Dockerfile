FROM python:3
RUN pip install flask

COPY ./app /app
COPY launch.py /
RUN mkdir /app/db
RUN mkdir /app/settings
WORKDIR /

CMD python3 launch.py
