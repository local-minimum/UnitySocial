
FROM python:3
RUN pip install flask

COPY app /app
COPY launch.py /
COPY templates /templates
RUN mkdir /app/db
RUN mkdir /app/settings
COPY system-tests/fixtures/settings.json /app/settings/settings.json
WORKDIR /

CMD python3 launch.py
