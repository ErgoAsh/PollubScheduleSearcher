# Main Dockerfile for deployment
FROM python:3.10-alpine

WORKDIR /usr/local/PollubScheduleSearcher

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY src .

CMD [ "python3", "src/__main__.py"]