FROM python:3.10-alpine

RUN adduser -D bot
USER bot
WORKDIR /home/bot

ENV PATH="${PATH}:/home/bot/.local/bin"

RUN /usr/local/bin/python -m pip install --user --upgrade pip

COPY --chown=bot:bot requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY --chown=bot:bot tg_bot.py tg_bot.py
COPY --chown=bot:bot moltin_api.py moltin_api.py
COPY --chown=bot:bot no_image.jpg no_image.jpg

CMD [ "python3", "tg_bot.py" ]
