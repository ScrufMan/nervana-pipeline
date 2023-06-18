FROM apache/tika:latest
USER root
RUN apt-get update -qqy \
  && apt-get -qqy install tesseract-ocr tesseract-ocr-eng tesseract-ocr-ces \
  && useradd --create-home tika
USER tika