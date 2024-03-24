FROM python
COPY . ./

RUN pip3 install --upgrade pip
RUN pip3 install fastapi
RUN pip3 install boto3

RUN apt update -y
RUN apt upgrade -y
RUN apt install curl -y

ENV topicArn= 

EXPOSE 80

ENTRYPOINT ["python", "Review.py"]