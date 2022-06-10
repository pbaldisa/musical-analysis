import spotipy
from spotipy.oauth2 import SpotifyOAuth
from fuzzywuzzy import fuzz
import pandas as pd
import socket
from urllib3.connection import HTTPConnection


def playlist_creator(n, m):
    list_of_songs = []
    # for each title in the csv col title
    for i in range(n, m):
        # reset the values
        max_value = 0
        curr_value = 0
        step = 0
        enter = 1
        # search a matching track in spotify, fetch only first five results
        results = spotifyObject.search(q=f"{songs_name_author['title'][i]} {songs_name_author['artist'][i]}", limit=5,
                                       type='track')  # get 5 responses since first isn't always accurate
        # if there aren't coincidences
        if results['tracks']['total'] == 0:  # if track isn't on spotify as queried
            enter = 0
            print("NOT FOUND: " + songs_name_author['title'][i] + songs_name_author['artist'][i])
            # exit if no coincidences

        # check again results after the if-nested-conditions
        if enter:
            # for each query returned from spotify, study max 5 possible matching tracks
            for j in range(len(results['tracks']['items'])):
                # if the substrings are similar ( > 90 )
                if fuzz.partial_ratio(results['tracks']['items'][j]['name'], songs_name_author['title'][i]) > 90 \
                        and fuzz.partial_ratio(results['tracks']['items'][j]['artists'][0]['name'],
                                               songs_name_author['artist'][i]) > 90:  # get
                    # right response by matching on artist and title
                    # we keep this track!
                    list_of_songs.append(results['tracks']['items'][j]['id'])  # append track id
                    print("Song " + results['tracks']['items'][j]['name'] + "added")
                    curr_value = -1
                    break  # don't want repeats of a sample ex: different versions

            if curr_value != -1:
                print("NOT FOUND: " + songs_name_author['title'][i] + songs_name_author['artist'][i])
                # exit if no coincidences

    prePlaylist = spotifyObject.user_playlists(user=username)
    playlist = prePlaylist["items"][0]["id"]

    # append the songs to the playlist
    while list_of_songs:
        spotifyObject.user_playlist_add_tracks(username, playlist, list_of_songs[:100], position=None)
        list_of_songs = list_of_songs[100:]


HTTPConnection.default_socket_options = (
            HTTPConnection.default_socket_options + [
            (socket.SOL_SOCKET, socket.SO_SNDBUF, 1000000), #1MB in byte
            (socket.SOL_SOCKET, socket.SO_RCVBUF, 1000000)
        ]
)
# per al cas de la popularity de les cançons dels artistes amb artist_hotness més elevat s'utilitza el dataset
# 'datasets/artists_hotness.csv'
df_csv = pd.read_csv('datasets/msd_reduced.csv')
# convert csv col author and title to dict
author_csv = {"artist": df_csv['artist_name'].tolist()}
title_csv = {"title": df_csv['title'].tolist()}
# merge dicts
songs_name_author = {**title_csv, **author_csv}
print(songs_name_author)
scope = "playlist-modify-public"
username = "fucyhdjvp8889yi08rjxwatno"
token = SpotifyOAuth(scope=scope, username=username)
spotifyObject = spotipy.Spotify(auth_manager=token)


for i in range(0, 55):
    playlist_name = str(i)
    playlist_description = "msd"
    # create empty playlist
    spotifyObject.user_playlist_create(user=username, name=playlist_name, public=True, description=playlist_description)
    try:
        playlist_creator(i*1000, i*1000 + 1000)
    # error per temps d'espera, que ho torni a intentar
    except socket.timeout:
        playlist_creator(i*1000, i*1000 + 1000)
