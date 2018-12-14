import requests
import os
import json


def get_config():
    with open('config.json', 'r') as config_file:
        return json.load(config_file)


def get_youtube_favourites(next_page_token=None, titles=list(), number_of_videos=0):
    global config
    config = get_config()
    url = 'https://www.googleapis.com/youtube/v3/playlistItems'
    params = {
        'part': 'snippet',
        'maxResults': 50,
        'playlistId': config['playlist_id'],
        'key': config['api_key']
    }

    if next_page_token is not None:
        params.update({'pageToken': next_page_token})

    response = requests.get(url, params).json()

    for item in response.get('items'):
        current_title = item['snippet']['title']
        if current_title == 'Private video':
            current_title += ' - ' + item['snippet']['resourceId']['videoId']
        titles.append(current_title)
        number_of_videos += 1

    print(f'writing batch {number_of_videos} of {response["pageInfo"]["totalResults"]}...')
    new_next_page_token = response.get('nextPageToken', None)

    if new_next_page_token is not None:
        new_next_page_token = response.get('nextPageToken')
        favourites = get_youtube_favourites(new_next_page_token, titles, number_of_videos)
        titles = favourites.get('titles')
        number_of_videos = favourites.get('videos')

    return {'titles': titles, 'videos': number_of_videos}


def write_favourites_to_file(destination, filename, titles, count):
    with open(os.path.join(destination, filename), 'wb') as file:
        file.write(f'Number of saved favourites videos {count}\n'.encode('utf-8'))
        for title in titles:
            file.write(title.encode('utf-8'))
            file.write(b'\n')


my_favourites = get_youtube_favourites()
write_favourites_to_file(
    config['destination_folder'],
    config['file_name'],
    my_favourites.get('titles'),
    my_favourites.get('videos')
)
