import os
import requests
import time
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

load_dotenv()

# Constants

PROMPT = "You are daily NBA podcaster. Given JSON data for a day of NBA games, write a script for a 5 minute podcast summarizing the most interesting things about the day's games. Try to be funny in weird. Give the players nicknames sometimes."
MODEL = "gpt-4-1106-preview"

DATE="2023-11-16"
NBA_STATS_BASE_URL = "https://api-nba-v1.p.rapidapi.com"

BASE_PATH = Path(__file__).parent

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

write_local_file(BASE_PATH / 'outputs/stats/' + DATE + '.json', games)

gameStats = []
for game in games['response']:
  time.sleep(.5)
  
  stats = get_nba_data('/players/statistics', {
    'game': game['id'],
  })

  gameStats.append(stats)

write_local_file(BASE_PATH / 'outputs/stats/' + game['id'] + '.json', stats)

# Generate script

client = OpenAI()

response = client.chat.completions.create(
  model=MODEL,
  messages=[
    {"role": "system", "content": PROMPT},
    {"role": "user", "content": "Game data: " + games + " Player game stats: " + stats},
  ]
)

script = response.choices[0].message.content

write_local_file(BASE_PATH / 'outputs/scripts/' + DATE + '.txt', script)

# Generate audio

speech_file_path = BASE_PATH / "outputs/audio/" + DATE + ".mp3"

response = client.audio.speech.create(
  model="tts-1",
  voice="onyx",
  input=script,
)

response.stream_to_file(speech_file_path)