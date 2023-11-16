# Daily NBA audio recap

Uses raw NBA stats data, pulled from [API-NBA on RapidApi](https://rapidapi.com/api-sports/api/api-nba/), and [OpenAI](https://openai.com/) services to generate an audio recap of a day of NBA games.

[Example audio output](https://www.timcieplowski.com/audio/ai_nba_recap_2023-11-14.mp3) for [Nov 14, 2023](https://www.nba.com/games?date=2023-11-14)

## Requirements

* Python
* PIP

## Install/setup

```
pip install -r requirements.txt
cp .env.example .env
```

Add values to `.env`.

## Run

Edit constants, at the top of `main.py`, as necessary, then:

```
python main.py
```

This will generate an `mp3` file, in `./outputs/audio/`.