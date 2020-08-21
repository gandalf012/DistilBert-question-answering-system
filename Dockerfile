FROM python:3.7-slim-buster
LABEL maintainer arnauld@southpigalle.io

RUN useradd worker

WORKDIR /worker

COPY --chown=worker:worker requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY --chown=worker:worker qa_interface.py .
COPY --chown=worker:worker data/ data/
COPY --chown=worker:worker models/ models/

USER worker
