import urllib.request
import re
import sys
import os
from pytube import YouTube
from youtube_title_parse import get_artist_title
import eyed3
import ampache
import time
import requests
import json

def clean(value):
    value = value.replace('\'','').replace('\"','').replace('’','').replace('$','S')
    return value

def get_video(track, album, artist, release_date, track_num, cover_photo):
    new_track = clean(track)
    new_album = clean(album)
    new_artist = clean(artist)
    query = new_track + ' ' + new_artist + ' lyrics'
    query = clean(query).replace(' ', '+')
    print(query)
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + query)
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    video_id = video_ids[0]
    artistExists = os.path.isdir('/home/files/Music/{0}'.format(new_artist))
    albumExists = os.path.isdir('/home/files/Music/{0}/{1}'.format(new_artist, new_album))
    if not artistExists:
        os.system('mkdir \"/home/files/Music/{0}\"; mkdir \"/home/files/Music/{0}/{1}\"'.format(new_artist, new_album))
    else:
        if not albumExists:
            os.system('mkdir \"/home/files/Music/{0}/{1}\"'.format(new_artist, new_album))
    location = '/home/files/Music/{0}/{1}'.format(new_artist, new_album)
    os.system('node /home/files/.scripts/music/youtube_mp3.js {0} \"{1}.mp3\" \"{2}\"'.format(video_id,track,location))

    file_location = location + '/' + track + '.mp3'
    audiofile = eyed3.load(file_location)
    audiofile.tag.title = track
    audiofile.tag.album = album
    audiofile.tag.artist = artist
    audiofile.tag.release_date = release_date
    audiofile.tag.recording_date = release_date
    audiofile.tag.track = track_num
    # audiofile.tag.images.set(img_url=cover_photo)

    audiofile.tag.save()

def download_track(id_):
    r = requests.get('https://api.spotify.com/v1/tracks/{0}'.format(id_), headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {token}'.format(token=access_token),
    })
    response = json.loads(r.text)
    # get album to get artist[0] name
    return response

def download_album(id_):
    r = requests.get('https://api.spotify.com/v1/albums/{0}'.format(id_), headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {token}'.format(token=access_token),
    })
    response = json.loads(r.text)
    return response

    for track in response['tracks']['items']:
        id2 = track['id']
    #return response

def download_artist(id_):
    albums = ''
    r = requests.get('https://api.spotify.com/v1/artists/{0}/albums'.format(id_), headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {token}'.format(token=access_token),
    })
    response = json.loads(r.text)

    for i in range(len(response['items'])):
        add = ','
        if i == len(response['items'])-1:
            add = ''
        albums += response['items'][i]['id'] + add
    r = requests.get('https://api.spotify.com/v1/albums?ids={0}'.format(albums), headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {token}'.format(token=access_token),
    })
    response = json.loads(r.text)

    for album in response['albums']:
        album_name = album['name']
        release_date = album['release_date']
        artist = album['artists'][0]['name']
        cover_art = album['images'][0]['url']
        for track in album['tracks']['items']:
            track_num = track['track_number']
            get_video(track['name'], album['name'], artist, release_date, track_num, cover_art)

music = []

id_file = open('/home/files/.scripts/music/choices.txt')
ids = id_file.readlines()
id_file.close()

choices_file = open('/home/files/.scripts/music/temp2.txt')
choices = choices_file.readlines()
choices_file.close()

access_token = ids[0].strip()

combined = ''
for i in range(1, len(ids)):
    combined += ids[i]

items = combined.split('\n\n')
for i in range(0, len(items)):
    array = items[i].split('\n')
    music.append(array[int(choices[i+1].strip()) - 1])

for value in music:
    split_value = value.split()
    id_ = split_value[0]
    music_type = split_value[1]

    if music_type == 'track':
        pass
        #download_track(id_)

    elif music_type == 'album':
        pass
        #download_album(id_)

    elif music_type == 'artist':
        #pass
        download_artist(id_)

    else:
        sys.exit()

"""



try:
    album = response['tracks']['items'][0]['album']['name']
    audiofile.tag.album = album
except KeyError:
    pass
if artist == '':
    try:
        artist = response['tracks']['items'][0]['artists'][0]['name']
    except KeyError:
        pass
audiofile.tag.artist = artist
audiofile.tag.title = title
audiofile.tag.recording_date = year

audiofile.tag.save()

command = 'get_cover_art --path ' + '\"/home/files/Music/' + title + '.mp3\"'
os.system(command)

os.system('rm -r temp.txt temp2.txt choices.txt _cover_art')
"""

"""
track = song['name']
album = song['album']['name']
artist = song['album']['artists'][0]['name']
release_date = song['album']['release_date']
image_url = song['album']['images'][0]['url']
"""
