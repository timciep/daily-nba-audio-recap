import os
import requests
import time
import json
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

load_dotenv()

# Constants

PROMPT = "You are daily NBA audio recap generator. Given JSON data for a day of NBA games, write a script for a 5 minute podcast summarizing the most interesting things about the day's games. Try to be funny and weird. Give the players (and not the teams) nicknames sometimes. Sometimes insult poor-performing players on the losing team."
MODEL = "gpt-4-1106-preview"
STATS_INFO = 'points = points, min = minutes played, fgm = field goals made, fga = field goals attempted, fgp = field goal percentage, ftm = free throws made, fta = free throws attempted, ftp = free throw percentage, tpm = three pointers made, tpa = three pointers attempted, tpp = three point percentage, offReb = offensive rebounds, defReb = defensive rebounds, totReb = total rebounds, assists = assists, pFouls = personal fouls, steals = steals, turnovers = turnovers, blocks = blocks, plusMinus = plus minus'

DATE="2023-11-17"
NBA_STATS_BASE_URL = "https://api-nba-v1.p.rapidapi.com"

BASE_PATH = str(Path(__file__).parent)

Path(BASE_PATH + '/outputs/stats').mkdir(parents=True, exist_ok=True)
Path(BASE_PATH + '/outputs/scripts').mkdir(parents=True, exist_ok=True)
Path(BASE_PATH + '/outputs/audio').mkdir(parents=True, exist_ok=True)

# Helper functions

def read_local_file(path):
  with open(path, 'r') as file:
    data = file.read().replace('\n', '')
  return data

def write_local_file(path, data):
  with open(path, 'w') as file:
    file.write(data)

def get_nba_data(path, query):
  url = NBA_STATS_BASE_URL + path
  headers = {
    'X-RapidAPI-Host': "api-nba-v1.p.rapidapi.com",
    'x-rapidapi-key': os.getenv('RAPID_API_KEY')
  }
  response = requests.request("GET", url, headers=headers, params=query)
  return response.json()


# Get data

games = get_nba_data('/games', {
  'league': 'standard',
  'date': DATE,
  'season': DATE[:4]
})

write_local_file(BASE_PATH + '/outputs/stats/' + DATE + '_raw.json', json.dumps(games))

gamesSimple = []
for game in games['response']:
  time.sleep(.5)

  stats = get_nba_data('/players/statistics', {
    'game': game['id'],
  })

  write_local_file(BASE_PATH + '/outputs/stats/' + DATE + '_' + str(game['id']) + '_raw.json', json.dumps(stats))

  playerStats = []
  for player in stats['response']:
    playerStats.append({
      'first_name': player['player']['firstname'],
      'last_name': player['player']['lastname'],
      'team': player['team']['name'],
      'position': player['pos'],
      'game_stats': {
        'points': player['points'],
        'minutes': player['min'],
        'fgm': player['fgm'],
        'fga': player['fga'],
        'fgp': player['fgp'],
        'ftm': player['ftm'],
        'fta': player['fta'],
        'ftp': player['ftp'],
        'tpm': player['tpm'],
        'tpa': player['tpa'],
        'tpp': player['tpp'],
        'offReb': player['offReb'],
        'defReb': player['defReb'],
        'totReb': player['totReb'],
        'assists': player['assists'],
        'pFouls': player['pFouls'],
        'steals': player['steals'],
        'turnovers': player['turnovers'],
        'blocks': player['blocks'],
        'plusMinus': player['plusMinus'],
      }
    })
  
  gamesSimple.append({
    'arena': game['arena']['name'],
    'city': game['arena']['city'] + ', ' + game['arena']['state'],
    'home_team_name': game['teams']['home']['name'],
    'away_team_name': game['teams']['visitors']['name'],
    'home_team_quarter_scores': game['scores']['home']['linescore'],
    'away_team_quarter_scores': game['scores']['visitors']['linescore'],
    'home_team_total_score': game['scores']['home']['points'],
    'away_team_total_score': game['scores']['visitors']['points'],
    'player_stats': playerStats,
  })

write_local_file(BASE_PATH + '/outputs/stats/' + DATE + '_simplified.json', json.dumps(gamesSimple))

# Generate script

client = OpenAI()

response = client.chat.completions.create(
  model=MODEL,
  messages=[
    {"role": "system", "content": PROMPT},
    {"role": "user", "content": "Stats abbreviations: " + STATS_INFO + " Game data: " + json.dumps(gamesSimple)},
  ]
)

script = response.choices[0].message.content

write_local_file(BASE_PATH + '/outputs/scripts/' + DATE + '.txt', script)

# Generate audio

speech_file_path = BASE_PATH + "/outputs/audio/" + DATE + ".mp3"

response = client.audio.speech.create(
  model="tts-1",
  voice="onyx",
  input=script,
)

response.stream_to_file(speech_file_path)