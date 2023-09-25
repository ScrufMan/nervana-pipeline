FROM apache/tika:latest-full
USER root
RUN apt-get update -qqy \
  && apt-get -qqy install python3 python3-pip \
  && apt-get -qqy install tesseract-ocr-* \
  && useradd --create-home tika

# python packages for tika image preprocessing
RUN pip3 install numpy
RUN pip3 install scikit-image

USER TIKA