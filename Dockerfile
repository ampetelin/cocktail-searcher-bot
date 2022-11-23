FROM python:3.9.15-slim
ENV PYTHONUNBUFFERED 1
WORKDIR /opt/cocktail-searcher-bot

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

COPY cocktail_searcher_bot .

CMD ["python", "main.py"]