FROM apache/tika:latest-full
USER root
RUN apt-get update -qqy \
  && apt-get -qqy install python3 python3-pip imagemagick tesseract-ocr-* \
  && useradd --create-home tika

# python packages for tika image preprocessing
RUN pip3 install numpy
RUN pip3 install scikit-image

# tesseract is prone to consume large amounts of computational resources
# we need to limit the number of threads it can use
# try to test with different values 2 works fine for 8 core cpu in the worst case scenario
ENV OMP_THREAD_LIMIT=1

USER tika