FROM python:3.8.5
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
COPY . ./
RUN chmod +x run_gunicorn.sh
ENTRYPOINT [ "./run_gunicorn.sh" ]