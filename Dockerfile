# An official Python runtime
FROM python:3.11.5-bookworm

WORKDIR /app

# Install system packages required for Tesseract, spaCy and Python-magic
# Then remove the package index cache to reduce image size
RUN apt-get update && apt-get install -y \
    curl \
    unzip unrar p7zip p7zip-full \
    tesseract-ocr \
    tesseract-ocr-all \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Download the model for Morphodita and save it in a temp directory
RUN mkdir -p /temp/ && \
    curl https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-4794/czech-morfflex2.0-pdtc1.0-220710.zip --output /temp/taggers.zip

# Unzip tagger and rename it to czech.tagger
RUN unzip -j /temp/taggers.zip czech-morfflex2.0-pdtc1.0-220710/czech-morfflex2.0-pdtc1.0-220710-pos_only.tagger -d /temp/ && \
    mv /temp/czech-morfflex2.0-pdtc1.0-220710-pos_only.tagger /temp/czech.tagger

# Copy the current directory contents into the container at /app
COPY . /app

# Move the tagger to the post_processor directory
RUN mv /temp/czech.tagger /app/entity_recognizer/post_processor/czech.tagger

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install spaCy models
RUN python -m spacy download en_core_web_trf
RUN python -m spacy download de_dep_news_trf

# Keep the container running
CMD ["tail", "-f", "/dev/null"]