import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import pandas as pd


def data_scraping(txt_uri):
    credentials = json.load(open('Authorization.json'))
    # own client id and client secret on the Spotify developers account
    client_id = credentials['client_id']
    client_secret = credentials['client_secret']

    client_credentials_manager = SpotifyOAuth(client_id=client_id, client_secret=client_secret)

    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    uri = "spotify:user:Test_1:playlist:" + txt_uri  # the URI is split by ':' to get the username and playlist ID
    username = uri.split(':')[2]
    playlist_id = uri.split(':')[4]

    results = sp.user_playlist_tracks(username, playlist_id)

    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    results = tracks

    for i in range(len(results)):
        print(i)  # counter
        if i == 0:
            playlist_tracks_id = results[i]['track']['id']
            playlist_tracks_titles = results[i]['track']['name']
            playlist_tracks_popularity = results[i]['track']['popularity']

            artist_list = results[i]['track']['artists'][0]['name']
            playlist_tracks_artists = artist_list

            features = sp.audio_features(playlist_tracks_id)
            features_df = pd.DataFrame(data=features, columns=features[0].keys())
            features_df['title'] = playlist_tracks_titles
            features_df['all_artists'] = playlist_tracks_artists
            features_df['popularity'] = playlist_tracks_popularity
            features_df = features_df[['title', 'all_artists', 'popularity']]
            continue
        else:
            try:
                playlist_tracks_titles = results[i]['track']['name']
                playlist_tracks_popularity = results[i]['track']['popularity']
                artist_list = results[i]['track']['artists'][0]['name']
                playlist_tracks_artists = artist_list
                new_row = {'title': [playlist_tracks_titles],
                           'all_artists': playlist_tracks_artists,
                           'popularity': [playlist_tracks_popularity],
                           }

                dfs = [features_df, pd.DataFrame(new_row)]
                features_df = pd.concat(dfs, ignore_index=True)
            except:
                continue

    return features_df


# introduïm l'uri de les playlists que vulguem scrapejar i s'itera per aquestes playlists per extreure la popularity
# hi haurien d'haver 55, però s'han fet en tongades de 10
playlist_uri = ["0sbQZYTeSvW7aVNmvPG7Hu", "0GaQzOEN4BcgSY3gFaQ8IX", "3KfWKZCXiNML1OF7YRQEpz", "44h58duCq21ChR2XXyJxuO",
                "1HhskSVcvRWqSvXmeLuuYy", "3NQEah47x473UdkKc2g8dA", "5KgDnBD1KvMu7CQUlb2SmO", "15Gjqvsxl7ilcZalgmdoud",
                "1oKIgGyxjWp79cuN0N8T1J", "1dMv1xrH6qDvt31E7Vce1t"]
indx = 0
for i in range(len(playlist_uri)):
    music_data = data_scraping(playlist_uri[i])
    # es genera el csv amb les cançons de la llista de reproducció i la seva popularity
    music_data.to_csv("spotify_" + str(indx) + ".csv", encoding='utf-8', index="false")
    indx += 1
