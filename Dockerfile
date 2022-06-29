FROM python:3.8.5
COPY requirements.txt ./
RUN pip3 install --user -r requirements.txt
COPY . ./
COPY run_server.sh ./
RUN chmod +x run_server.sh
EXPOSE 80
ENTRYPOINT [ "./run_server.sh" ]