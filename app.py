import os
import requests
from dotenv import load_dotenv
import pandas as pd
from matplotlib import pyplot as plt

load_dotenv()

def get_words():
    word_input = ''
    while word_input == '':
        word_input = input('Write the two words you want to search for separated by an empty space: ')

    words = word_input.split(' ')
    return words

def request_api(word_search):
    api_key = os.getenv('API_KEY')
    type_search = 'video'
    part_search = 'snippet'
    token = ''
    videos_list = []

    response = requests.get(
        f'https://www.googleapis.com/youtube/v3/search?key={api_key}&orderby=published&type={type_search}&part={part_search}&q={word_search}&maxResults=50&pageToken={token}')

    response_js = response.json()
    videos_list.extend(response_js['items'])
    counter = 1

    # while counter < 10:
    while counter < 3:
        if response_js['nextPageToken']:
            token = response_js['nextPageToken']
        else:
            token = ''

        if token == '':
            break

        response = requests.get(
            f'https://www.googleapis.com/youtube/v3/search?key={api_key}&orderby=published&type={type_search}&part={part_search}&q={word_search}&maxResults=50&pageToken={token}')

        print(f'Requesting page {counter}; Token = {token}')
        response_js = response.json()
        videos_list.extend(response_js['items'])
        counter += 1

    return videos_list

def get_videos(response):
    temp_video_list = []

    for item in response:
        video = {
            'channel_id': item['snippet']['channelId'],
            'channel_title': item['snippet']['channelTitle'],
            'vid_title': item['snippet']['title'],
            'vid_date_public': item['snippet']['publishedAt'],
            'vid_url': 'https://www.youtube.com/watch?v=' + item['id']['videoId']
        }
        temp_video_list.append(video)
    return temp_video_list

def get_requests(word_1, word_2):
    res_request = []

    data_1 = request_api(word_1)
    data_2 = request_api(word_2)

    res_request.append(data_1)
    res_request.append(data_2)

    return res_request

def parse_videos_list(list_1, list_2):
    list_parsed = []

    vd_list_1 = get_videos(list_1)
    vd_list_2 = get_videos(list_2)

    list_parsed.append(vd_list_1)
    list_parsed.append(vd_list_2)

    return list_parsed

word1, word2 = get_words()
list_requests = get_requests(word1, word2)
request_1, request_2 = list_requests

videos_parsed = parse_videos_list(request_1, request_2)
videos_list_1, videos_list_2 = videos_parsed

# DATA ANALYSIS
# word1
df_word1 = pd.DataFrame(videos_list_1)
df_word1.columns = ['Channel Id', 'Channel Title', 'Video Title', 'Publication date', 'URL']
df_word1['Publication date'] = pd.to_datetime(df_word1['Publication date'])
df_word1['Publication date'] = df_word1['Publication date'].dt.year
videos_by_year_word1 = df_word1.groupby('Publication date').size().reset_index()

# word2
df_word2 = pd.DataFrame(videos_list_2)
df_word2.columns = ['Channel Id', 'Channel Title', 'Video Title', 'Publication date', 'URL']
df_word2['Publication date'] = pd.to_datetime(df_word2['Publication date'])
df_word2['Publication date'] = df_word2['Publication date'].dt.year
videos_by_year_word2 = df_word2.groupby('Publication date').size().reset_index()

# Graphs
# absolute counts of videos published by year
videos_by_year_word1.rename(columns={'Publication date': 'year', 0: 'count'}, inplace=True)
videos_by_year_word2.rename(columns={'Publication date': 'year', 0: 'count'}, inplace=True)
plt.plot(videos_by_year_word1['year'], videos_by_year_word1['count'])
plt.plot(videos_by_year_word2['year'], videos_by_year_word2['count'])
plt.title(f'Number of videos published per subject: {word1} X {word2}')
plt.grid(True)
plt.legend([word1, word2])
plt.xlabel('Year')
plt.ylabel('Absolute count')
plt.savefig('images/absolute_counts.png')

# % of videos published by year
videos_by_year_word1['perc_vid'] = videos_by_year_word1['count'] / videos_by_year_word1['count'].iloc[0] * 100
videos_by_year_word2['perc_vid'] = videos_by_year_word2['count'] / videos_by_year_word2['count'].iloc[0] * 100
plt.plot(videos_by_year_word1['year'], videos_by_year_word1['perc_vid'])
plt.plot(videos_by_year_word2['year'], videos_by_year_word2['perc_vid'])
plt.title(f'Percentage of videos published per subject: {word1} X {word2}')
plt.grid(True)
plt.legend([word1, word2])
plt.xlabel('Year')
plt.ylabel('% of publication')
plt.savefig('images/percentage.png')

df_word1.to_csv('results-word1.csv', index=False)
df_word2.to_csv('results-word2.csv', index=False)

print(f'DataFrames: \n {df_word1} {df_word2}')
