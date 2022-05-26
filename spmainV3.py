'''
Author: Neel Joshi

*hopefully not too flawed version

General outline-

- get user input for track name and artist
- confirm if the track is correct-- else keep going through searches

- get track audio features

- classify song under genre(s)

- for all genres, for songs in playlists, extract song features for all songs
- find the mean and std dev for each feature
- subtract the z scores for the features of the given songs from the z scores for each feature of each song
- rank each a score difference in ascending order
- find the avg rank of features for all songs
- sort the avg rank of features

- output 50 lowest aavg ranks

'''

import spotipy
import math
from spotipy.oauth2 import SpotifyClientCredentials

#*****************************
# CLIENT_ID = your client ID for the spotify api project
# CLIENT_SECRET = your client secret for the spotify api project
#*****************************

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


mean_distance = [0,0,0,0,0,0,0,0,0]

songs = []
song_count = 0;

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
                print("Error in getting song")
                continue

            if temp_song_id not in songs:
                songs.append(temp_song_id)

                try:
                    temp_features = spotify.audio_features(temp_song_id)[0]
                except:
                    songs.pop(len(songs)-1)
                    continue
                
                try:
                    danceability.append((temp_features["danceability"] ))
                    mean_distance[0] += danceability[song_count]

                    energy.append((temp_features["energy"] ))
                    mean_distance[1] += energy[song_count]

                    loudness.append((temp_features["loudness"] ))
                    mean_distance[2] += loudness[song_count]

                    speechiness.append((temp_features["speechiness"] ))
                    mean_distance[3] += speechiness[song_count]

                    acousticness.append((temp_features["acousticness"]))
                    mean_distance[4] += acousticness[song_count]

                    instrumentalness.append((temp_features["instrumentalness"]))
                    mean_distance[5] += instrumentalness[song_count]

                    liveness.append((temp_features["liveness"] ))
                    mean_distance[6] += liveness[song_count]

                    valence.append((temp_features["valence"]))
                    mean_distance[7] += valence[song_count]

                    tempo.append((temp_features["tempo"]  ))
                    mean_distance[8] += tempo[song_count]

                    song_count = song_count + 1
                except:  #POSSIBLE PROBLEM HERE
                    print("problem accessing one of the features-> might affect the list of features")
                    songs.pop(len(songs)-1)
                    continue
        
        
    print("----")

print(song_count)
for t in range (0, 9):
    mean_distance[t] /= song_count


#takes std dev of the data
stdev_distance = [0,0,0,0,0,0,0,0,0]

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

#given z scores

given_zd  = (song_features["danceability"] - mean_distance[0]) / stdev_distance[0] 
given_ze  = (song_features["energy"] - mean_distance[1]) / stdev_distance[1] 
given_zl  = (song_features["loudness"] - mean_distance[2]) / stdev_distance[2] 
given_zs  = (song_features["speechiness"] - mean_distance[3]) / stdev_distance[3] 
given_za  = (song_features["acousticness"] - mean_distance[4]) / stdev_distance[4] 
given_zi  = (song_features["instrumentalness"] - mean_distance[5]) / stdev_distance[5] 
given_zli = (song_features["liveness"] - mean_distance[6]) / stdev_distance[6] 
given_zv  = (song_features["valence"] - mean_distance[7]) / stdev_distance[7] 
given_zt  = (song_features["tempo"] - mean_distance[8]) / stdev_distance[8] 

#z scores for searched songs

zd_dict = {}
ze_dict = {}
zl_dict = {}
zs_dict = {}
za_dict = {}
zi_dict = {}
zli_dict = {}
zv_dict = {}
zt_dict = {}

avg_z_dict = {}

#finding difference between given z score and song z score for each feature of each song
for i in range (0, song_count):

    zd  = (danceability[i] - mean_distance[0]) / stdev_distance[0] 
    ze  = (energy[i] - mean_distance[1]) / stdev_distance[1] 
    zl  = (loudness[i] - mean_distance[2]) / stdev_distance[2] 
    zs  = (speechiness[i] - mean_distance[3]) / stdev_distance[3] 
    za  = (acousticness[i] - mean_distance[4]) / stdev_distance[4] 
    zi  = (instrumentalness[i] - mean_distance[5]) / stdev_distance[5] 
    zli = (liveness[i] - mean_distance[6]) / stdev_distance[6] 
    zv  = (valence[i] - mean_distance[7]) / stdev_distance[7] 
    zt  = (tempo[i] - mean_distance[8]) / stdev_distance[8] 

    zd_dict[songs[i]] = abs(given_zd - zd)
    ze_dict[songs[i]] = abs(given_ze - ze)
    zl_dict[songs[i]] = abs(given_zl - zl)
    zs_dict[songs[i]] = abs(given_zs - zs)
    za_dict[songs[i]] = abs(given_za - za)
    zi_dict[songs[i]] = abs(given_zi - zi)
    zli_dict[songs[i]] = abs(given_zli - zli)
    zv_dict[songs[i]] = abs(given_zv - zv)
    zt_dict[songs[i]] = abs(given_zt - zt)

    avg_z_dict[songs[i]] = 1

#sorting the difference and ranking
sorted_zd_list  = list(sorted(zd_dict.items(),  key=lambda x: x[1]))
sorted_ze_list  = list(sorted(ze_dict.items(),  key=lambda x: x[1]))
sorted_zl_list  = list(sorted(zl_dict.items(),  key=lambda x: x[1]))
sorted_zs_list  = list(sorted(zs_dict.items(),  key=lambda x: x[1]))
sorted_za_list  = list(sorted(za_dict.items(),  key=lambda x: x[1]))
sorted_zi_list  = list(sorted(zi_dict.items(),  key=lambda x: x[1]))
sorted_zli_list = list(sorted(zli_dict.items(), key=lambda x: x[1]))
sorted_zv_list  = list(sorted(zv_dict.items(),  key=lambda x: x[1]))
sorted_zt_list  = list(sorted(zt_dict.items(),  key=lambda x: x[1]))

#finding avg rank
for i in range (0, len(sorted_zd_list)):
    
    avg_z_dict[sorted_zd_list[i][0]] = i + avg_z_dict[sorted_zd_list[i][0]]
    avg_z_dict[sorted_ze_list[i][0]] = i + avg_z_dict[sorted_ze_list[i][0]]
    avg_z_dict[sorted_zl_list[i][0]] = i + avg_z_dict[sorted_zl_list[i][0]]
    avg_z_dict[sorted_zs_list[i][0]] = i + avg_z_dict[sorted_zs_list[i][0]]
    avg_z_dict[sorted_za_list[i][0]] = i + avg_z_dict[sorted_za_list[i][0]]
    avg_z_dict[sorted_zi_list[i][0]] = i + avg_z_dict[sorted_zi_list[i][0]]
    avg_z_dict[sorted_zli_list[i][0]] = i + avg_z_dict[sorted_zli_list[i][0]]
    avg_z_dict[sorted_zv_list[i][0]] = i + avg_z_dict[sorted_zv_list[i][0]]
    avg_z_dict[sorted_zt_list[i][0]] = i + avg_z_dict[sorted_zt_list[i][0]]


#sorting avg rank
sorted_z_dict = sorted(avg_z_dict.items(),  key=lambda x: x[1])


print(len(sorted_z_dict))


#printing lowest 50 avg ranks
sorted_z_list = list(sorted_z_dict)[:50]

for x in sorted_z_list:
    current_rec = spotify.track(x[0], market="US")
    print(current_rec["name"]+ " " + current_rec["artists"][0]["name"])