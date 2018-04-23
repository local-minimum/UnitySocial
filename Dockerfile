FROM py3
pip install flask

COPY app.py /app/app.py
RUN mkdir /app/db
RUN mkdir /app/settings
WORKDIR /app

CMD python3 app.py
