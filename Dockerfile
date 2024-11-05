FROM brendoncintas/spellbreak_game_server

WORKDIR /spellbreak-server/spellbreak-server

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "-m", "server.server"]
