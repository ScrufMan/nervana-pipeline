# An official Python runtime
FROM python:3.11.5-bookworm

WORKDIR /app

# Install system packages required for Tesseract, spaCy and Python-magic
# Then remove the package index cache to reduce image size
RUN apt-get update && apt-get install -y \
    curl \
    unzip unrar-free p7zip p7zip-full \
    tesseract-ocr \
    tesseract-ocr-all \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# install spacy language models
RUN python -m spacy download fr_core_news_sm
RUN python -m spacy download pl_core_news_sm
RUN python -m spacy download ru_core_news_sm
RUN python -m spacy download it_core_news_sm
RUN python -m spacy download da_core_news_sm
RUN python -m spacy download pt_core_news_sm
RUN python -m spacy download sv_core_news_sm
RUN python -m spacy download ro_core_news_sm

# Copy the current directory contents into the container at /app
COPY . /app

# Keep the container running
CMD ["tail", "-f", "/dev/null"]