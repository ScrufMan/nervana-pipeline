FROM apache/tika:latest-full
USER root
RUN apt-get update -qqy \
  && apt-get -qqy install tesseract-ocr-ces tesseract-ocr-rus tesseract-ocr-slk  \
    tesseract-ocr-bel   tesseract-ocr-chi-sim   tesseract-ocr-chi-tra \
  && useradd --create-home tika
USER tika