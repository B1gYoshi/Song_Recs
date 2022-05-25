'''
Author: Neel Joshi

*flawed version

General outline-

- get user input for track name and artist
- confirm if the track is correct-- else keep going through searches

- get track audio features

- classify song under genre(s)

- for all genres, for songs in playlists, extract song features for all songs
- find the mean and std dev for each feature
- find the z scores for the features of the given songs and for each feature of each song
- find the avg z score of each feature of the given song and the other songs
- sort the avg z scores

- output 50 lowest z score avgs

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
                    print("problem accessing one of the features- feature count wack")
                    songs.pop(len(songs)-1)
                    continue
        
        
    print("----")

print(song_count)
for t in range (0, 9):
    mean_distance[t] /= song_count


#takes std dev of the features
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

given_mean_z = (given_zd+given_ze+given_zl+given_zs+given_za+given_zi+given_zli+given_zv+given_zt) / 9

#z scores for searched songs

# generally something wrong with using means like this cuz mean of 1, -1 = mean of 500, -500 but these params are not similar at all

z_distance = []

z_dict = {}

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

    mean_z = (zd+ze+zl+zs+za+zi+zli+zv+zt) / 9

    z_distance.append(abs(mean_z-given_mean_z))
    z_dict[songs[i]] = z_distance[i]

#sort songs in ascending order using z_distance
sorted_z_dict = sorted(z_dict.items(), key=lambda x: x[1])

print(len(sorted_z_dict))

sorted_z_list = list(sorted_z_dict)[:50]

for x in sorted_z_list:
    current_rec = spotify.track(x[0], market="US")
    print(current_rec["name"]+ " " + current_rec["artists"][0]["name"])