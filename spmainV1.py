'''

Author: Beeg Yoshi

The plan is simple

- get user input for track name
- confirm if the track is correct-- else keep going through searches

- extract important track data 
    - genre**

- get mean and std dev of difference from 


-do search based on genres extracted
TBD

'''

#trying to commit and push

print("hi")

#find way to import client_id and client_secret from another file

import spotipy
import math
from spotipy.oauth2 import SpotifyClientCredentials

# CLIENT_ID = your client ID for the spotify api project
# CLIENT_SECRET = your client secret for the spotify api project

spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

user_input = input("Enter a song and its artist: ")

query_search_results = spotify.search(q = user_input, type = 'track', limit = 10, offset= 0)

i = 0
found = False
song_id = ""
song_name = ""
song_info = {}

while (i < 10 and not found):
    
    song_id = query_search_results["tracks"]["items"][i]["id"]
    song_info = spotify.track(song_id, market="US")
    song_name = song_info["name"] +  " in the album " + song_info["album"]["name"]

    print(song_name)
    correct = int(input("If the track above is the one you are looking for, enter 1. Enter any other number otherwise: "))
    print()

    if (correct == 1):
        found = True
    
    i = i+1

#needs to be tested
if (i == 10):
    exit()

artist_id = song_info["artists"][0]["id"]

song_features = spotify.audio_features(song_id)[0]


#print (song_analysis)


genres = spotify.artist(artist_id)["genres"]
print(genres)

#check with user if they like the genres

j = 0

while j < len(genres) :

    valid_genre = int(input(genres[j] + " <- does this genre describe your song (y=1, n=0): "))

    if (valid_genre == 0):
        genres.pop(j)
    else:      
        j = j + 1

print(genres)

#let user add more genres
genres_added = False

while (not genres_added):

    genre_to_add = input("Enter a genre you would classify this song under (none to stop): ")

    if (genre_to_add == "none"):
        genres_added = True
    else:
        genres.append(genre_to_add)


print(genres)

# 0 - danceability
danceability = []
# 1 - energy
energy = []
# 2 - loudness
loudness = []
# 3 - speechiness
speechiness = []
# 4 - acousticness
acousticness = []
# 5 - instrumentalness
instrumentalness = []
# 6 - liveness
liveness = []
# 7 - valence
valence = []
# 8 - temp0
tempo = []


mean_distance = []
for t in range (0, 9): mean_distance.append(0)


#TESTING WITH ONE GENRE

#genre_specific_playlist = spotify.search(q = genres[0], type = "playlist", limit = 50, offset=0)

#playlist_1 = genre_specific_playlist["playlists"]["items"][10]["id"]

#print(playlist_1)

songs = []
song_count = 0;

#at least one of the artists works has to be in the playlist 

#NONE TYPE ERROR IN INNER 3RD LOOP

for x in range(0, len(genres)): #for all genres

    playlists_for_genre = spotify.search(q = genres[x], type = "playlist", limit = 50, offset=0)

    total_items = len(playlists_for_genre["playlists"]["items"])
    print(total_items)



    for j in range (0,total_items): # for all playlists in that genre

        playlist_id = playlists_for_genre["playlists"]["items"][j]["id"]
        #the_playlist = spotify.playlist(playlist_id)
        
        playlist_items = spotify.playlist_tracks(playlist_id)
        playlist_size = len(playlist_items["items"])

        if playlist_size > 20: playlist_size = 20

        for k in range (0, playlist_size): # for all songs in that playlist
            try:
                temp_song_id = playlist_items["items"][k]["track"]["id"]
            except:
                print("bruh")
                continue
            if temp_song_id not in songs:
                songs.append(temp_song_id)

                try:
                    temp_features = spotify.audio_features(temp_song_id)[0]
                except:
                    songs.pop(len(songs)-1)
                    continue
                
                try:
                    danceability.append(abs(temp_features["danceability"] - song_features["danceability"]))
                    mean_distance[0] += danceability[song_count]

                    energy.append(abs(temp_features["energy"] - song_features["energy"]))
                    mean_distance[1] += energy[song_count]

                    loudness.append(abs(temp_features["loudness"] - song_features["loudness"]))
                    mean_distance[2] += loudness[song_count]

                    speechiness.append(abs(temp_features["speechiness"] - song_features["speechiness"]))
                    mean_distance[3] += speechiness[song_count]

                    acousticness.append(abs(temp_features["acousticness"] - song_features["acousticness"]))
                    mean_distance[4] += acousticness[song_count]

                    instrumentalness.append(abs(temp_features["instrumentalness"] - song_features["instrumentalness"]))
                    mean_distance[5] += instrumentalness[song_count]

                    liveness.append(abs(temp_features["liveness"] - song_features["liveness"]))
                    mean_distance[6] += liveness[song_count]

                    valence.append(abs(temp_features["valence"] - song_features["valence"]))
                    mean_distance[7] += valence[song_count]

                    tempo.append(abs(temp_features["tempo"] - song_features["tempo"]))
                    mean_distance[8] += tempo[song_count]

                    song_count = song_count + 1
                except:
                    songs.pop(len(songs)-1)
                    continue
        
        
    print("----")
print(song_count)
for t in range (0, 9):
    mean_distance[t] /= song_count


#Lol this isn't normal distribution– its skewed left or right but whatever

stdev_distance = []
for i in range (0,9): stdev_distance.append(0)

for i in range (0, song_count):

    stdev_distance[0] += (danceability[i] - mean_distance[0]) **2
    stdev_distance[1] += (energy[i] - mean_distance[1]) **2
    stdev_distance[2] += (loudness[i] - mean_distance[2]) **2
    stdev_distance[3] += (speechiness[i] - mean_distance[3]) **2
    stdev_distance[4] += (acousticness[i] - mean_distance[4]) **2
    stdev_distance[5] += (instrumentalness[i] - mean_distance[5]) **2
    stdev_distance[6] += (liveness[i] - mean_distance[6]) **2
    stdev_distance[7] += (valence[i] - mean_distance[7]) **2
    stdev_distance[8] += (tempo[i] - mean_distance[8]) **2

for i in range (0, 9):
    stdev_distance[i] = math.sqrt( stdev_distance[i] / song_count  )

#take avg of zscore 

z_distance = []

z_dict = {}

for i in range (0, song_count):

    zd  = abs(danceability[i] - mean_distance[0]) / stdev_distance[0] 
    ze  = abs(energy[i] - mean_distance[1]) / stdev_distance[1] 
    zl  = abs(loudness[i] - mean_distance[2]) / stdev_distance[2] 
    zs  = abs(speechiness[i] - mean_distance[3]) / stdev_distance[3] 
    za  = abs(acousticness[i] - mean_distance[4]) / stdev_distance[4] 
    zi  = abs(instrumentalness[i] - mean_distance[5]) / stdev_distance[5] 
    zli = abs(liveness[i] - mean_distance[6]) / stdev_distance[6] 
    zv  = abs(valence[i] - mean_distance[7]) / stdev_distance[7] 
    zt  = abs(tempo[i] - mean_distance[8]) / stdev_distance[8] 

    mean_z = (zd+ze+zl+zs+za+zi+zli+zv+zt) / 9

    z_distance.append(mean_z)
    z_dict[songs[i]] = mean_z

#sort songs in ascending order using z_distance
sorted_z_dict = sorted(z_dict.items(), key=lambda x: x[1])

print(len(sorted_z_dict))

sorted_z_list = list(sorted_z_dict)[:50]

for x in sorted_z_list:
    current_rec = spotify.track(x[0], market="US")
    print(current_rec["name"]+ " " + current_rec["artists"][0]["name"])