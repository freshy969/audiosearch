import random

# bios = list of artist biographies (dict)
# return wikipedia bio
#
# (todo ?): if wikibio does not exist, attempt to find a bio with: min < len (bio) < max 
def get_good_bio(bios):
    for b in bios:    
        if str(b['site']) == 'wikipedia':
            return b['text']

    return 'Artist biography is not available.'


# songs = incoming list of songs
# n = size of returned list
#
# remove duplicates (based on artist_id) and return list of size n
# if len (songs) < n, return list of size len (songs)
def remove_duplicates (songs, n):
    unique = []
    temp = {}

    for s in songs:
        t = s.title.lower(), s.artist_id

        if t not in temp:
            temp[t] = s
            unique.append(s)

        if len(unique) == n:
            break

    return unique


# artists = top 10 similar artists
# similar = list containing 10 randomly chosen songs
#
# create a list containing three songs from each similar artist
# note: this assumes best case of each artist having >= 3 songs
def get_similar_songs(artists):
    similar = []
    temp = {}
    count = 0

    for a in artists:

        # boundary check
        if len(a.songs) < 3:
            song_range = len(a.songs)
        else:
            song_range = 3

        # build dict
        for x in range(0, song_range):  
            temp[count] = a.songs[x]
            count += 1

    # randomly build return list
    for x in range(0, 10):
        key = random.choice (temp.keys())
        s = temp[key]

        similar.append(s)
        del temp[key]

    return similar