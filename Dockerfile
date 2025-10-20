FROM python:3.12.12-bookworm

WORKDIR /lexiloop

# Add gunicorn and psycopg2 (for PostgreSQL) to your requirements.txt
# Gunicorn is your production server.
# Boto3 is for AWS Secrets Manager.
# Psycopg2-binary is the driver for PostgreSQL (RDS).
COPY ./requirements.txt /lexiloop/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /lexiloop/requirements.txt

# Use this instead of downloading in main.py
RUN apt-get update && apt-get install -y wget unzip && \
    mkdir -p /root/nltk_data/tokenizers && \
    wget -q https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers/punkt.zip -O /root/nltk_data/tokenizers/punkt.zip && \
    unzip -q /root/nltk_data/tokenizers/punkt.zip -d /root/nltk_data/tokenizers/ && \
    rm /root/nltk_data/tokenizers/punkt.zip && \
    \
    mkdir -p /root/nltk_data/taggers && \
    wget -q https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/taggers/averaged_perceptron_tagger.zip -O /root/nltk_data/taggers/averaged_perceptron_tagger.zip && \
    unzip -q /root/nltk_data/taggers/averaged_perceptron_tagger.zip -d /root/nltk_data/taggers/ && \
    rm /root/nltk_data/taggers/averaged_perceptron_tagger.zip && \
    \
    mkdir -p /root/nltk_data/corpora && \
    wget -q https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/wordnet.zip -O /root/nltk_data/corpora/wordnet.zip && \
    unzip -q /root/nltk_data/corpora/wordnet.zip -d /root/nltk_data/corpora/ && \
    rm /root/nltk_data/corpora/wordnet.zip && \
    apt-get remove -y wget unzip && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

COPY ./app /lexiloop/app

EXPOSE 80

# Use Gunicorn to run your app
# -w 4: Starts 4 "worker" processes to handle traffic.
# -k uvicorn.workers.UvicornWorker: Tells Gunicorn to use Uvicorn.
# app.main:app: Points to the 'app' variable inside your 'app/main.py' file.
# -b 0.0.0.0:80: Binds to all network interfaces on port 80.
CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "-b", "0.0.0.0:80"]