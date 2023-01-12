FROM python
COPY *.py .
COPY config.json .
RUN pip install aiogram transformers torch
ENTRYPOINT ["python", "bot.py"]