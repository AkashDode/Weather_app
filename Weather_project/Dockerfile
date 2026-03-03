#Use official Python image

FROM python:3.12-slim

#Set environment variables to optimize Python

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

#Set working directory inside container

WORKDIR /app

#Copy dependencies file

COPY requirements.txt /app/

#Install dependencies

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

#Copy the whole project into container

COPY . /app/

#Expose the port Django will run on

EXPOSE 8000

#Command to run Django server

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
