FROM python:3.5
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y r-base r-base-dev libreadline-dev
# TODO: Add R deps for the old analytics page maybe if it's still needed
RUN mkdir /usr/local/declarations_site
COPY requirements.txt /usr/local/declarations_site/
WORKDIR /usr/local/declarations_site
RUN pip3 install -r requirements.txt
RUN apt-get purge -y r-base-dev libreadline-dev
COPY declarations_site /usr/local/declarations_site
RUN apt-get install -y ruby-sass
