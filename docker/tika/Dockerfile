FROM apache/tika:latest-full
USER root
RUN apt-get update -qqy \
  && apt-get -qqy install tesseract-ocr-* \
  && useradd --create-home tika
USER tika