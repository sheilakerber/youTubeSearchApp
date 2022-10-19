import os
import requests
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

def search_word():
    word_input = ''
    while word_input == '':
        word_input = input('Write the word you want to search for: ')
    return word_input

videos_list = []

def request_api(word_search):
    api_key = os.getenv('API_KEY')
    type_search = 'video'
    part_search = 'snippet'
    token = ''

    response = requests.get(
        f'https://www.googleapis.com/youtube/v3/search?key={api_key}&orderby=published&type={type_search}&part={part_search}&q={word_search}&maxResults=50&pageToken={token}')

    response_js = response.json()
    videos_list.extend(response_js['items'])
    counter = 1

    while counter < 10:
        if response_js['nextPageToken']:
            token = response_js['nextPageToken']
        else:
            token = ''
        print(f'Requesting page {counter}; Token = {token}')

        if token == '':
            break

        response = requests.get(
            f'https://www.googleapis.com/youtube/v3/search?key={api_key}&orderby=published&type={type_search}&part={part_search}&q={word_search}&maxResults=50&pageToken={token}')

        response_js = response.json()
        videos_list.extend(response_js['items'])
        counter += 1

    return videos_list

def get_videos(response):
    temp_video_list = []

    for item in response:
        video = {
            'vid_title': item['snippet']['title'],
            'vid_date_public': item['snippet']['publishedAt'],
            'vid_url': 'https://www.youtube.com/watch?v=' + item['id']['videoId']
        }
        temp_video_list.append(video)
    return temp_video_list

word = search_word()
data = request_api(word)
final_videos_list = get_videos(data)

df_data = pd.DataFrame(final_videos_list)
df_data.columns = ['Title', 'Publication date', 'URL']
df_data.to_csv('results.csv', index=False)

print(f'DataFrame with the results: \n {df_data}')
