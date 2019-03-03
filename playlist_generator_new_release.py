import spotipy 
import spotipy.util as util
import pandas as pd
import math as math
import datetime
from collections import Counter

####################################################
#           CONFIGURATION
####################################################
username = 'a0092165'
start_search_date = '2019-01-17'

# artists with genre in the below list will be EXCLUDED
genres_to_exclude = ['pop', 'rap', 'hip hop',
                     'classical','opera','baroque','choral','violin','viola','cello',
                     'orchestral','orchestra','disney','chanson','cabaret','celtic',
                     'early music ensemble','romantic era','focus',
                     'scorecore', 'soundtrack', # ????,
                     'big room', 'broadway', 'hollywood','chamber orchestra','classify']

# artists with below genres will be REVIVED if they are excludes in above list
genres_to_reinclude = ['metal']

# below artists will always be included in new release search
must_include_artists = ['Adam Lambert', 'Hans Zimmer', 
                        'Landon Tewers', 'D. Randall Blythe', 
                        'Venom Inc.', 'THRON'] # even if hit kill keywords...

# track name to exclude when creating new playlist: TOP PRIORITY RULE
key_words_exclude_trackname = ['live in','live at','remaster','remastered','remix']

# artists with more than this threshold artists with my universe, will be included as well
threshold_related = 8

create_genre_csv = True
create_track_csv = True

####################################################
#           INITIALIZE
####################################################


def format_genres(list_of_genres, nchar=67):
    if len(list_of_genres) <= 5:
        return ', '.join(list_of_genres)+','
    else:
        temp_str = ''
        for i in range(math.floor(len(list_of_genres)/5)+1):
            temp_list = list_of_genres[(i*5):min(len(list_of_genres), (i*5+5))]
            if len(temp_list) > 0:
                temp_str = temp_str + ', '.join(temp_list) + ',\n' + ' '*nchar
        return temp_str[:-(2+nchar)]


def new_artist_entry(name = [], artist_id = [], uri = [], playlist = [], track_name = []):
    return {'name':name, 
            'id': artist_id, 
            'uri': uri, 
            'playlist':playlist, 
            'track_name':track_name}
 
def artist_entry_from_track(track = {}, playlist_name = ''):
    n_artists = len(track['artists'])
    return new_artist_entry(name = [this_artist['name'] for this_artist in track['artists']], 
                            artist_id = [this_artist['id'] for this_artist in track['artists']], 
                            uri = [this_artist['uri'] for this_artist in track['artists']], 
                            playlist = [playlist_name] * n_artists, 
                            track_name = [track['name']] * n_artists)
    
def artist_entry_from_artist(artist = {}, playlist_name = '', track_name = ''):
    return new_artist_entry(name = [artist['name']], 
                            artist_id = [artist['id']], 
                            uri = [artist['uri']], 
                            playlist = [playlist_name], 
                            track_name = [track_name]) 
       
    
def new_track_entry(id = [], name = [], artist = [], analysis_url = [],
                    acousticness = [], danceability = [],
                    duration_ms = [], tempo = [],
                    energy = [], instrumentalness = [], key = [],
                    liveness = [], loudness = [], mode = [], speechiness = [],
                    time_signature = [],
                    track_href = [], type = [], uri = [],
                    valence = [], popularity = [], 
                    reason_added = []):   
    return {'id' : id, 
            'uri' : uri,
            'track_href' : track_href,   
            'name' : name, 
            'type' : type,    
            'artist' : artist,
            # hard facts
            'duration_ms' : duration_ms,
            'key' : key,
            'tempo' : tempo,
            'time_signature' : time_signature,
            # more subjective
            'acousticness' : acousticness,       
            'danceability' : danceability,            
            'energy' : energy,
            'instrumentalness' : instrumentalness,            
            'liveness' : liveness,
            'loudness' : loudness,
            'mode' : mode,
            'speechiness' : speechiness,
            'valence' : valence,
            'popularity' : popularity,
            'analysis_url' : analysis_url,
            'reason_added' : reason_added}
    
def track_entry(track = {}, this_feature = {}, reason = ''):
    f_temp = new_track_entry(id=[track['id']], 
                             name=[track['name']],
                             artist=[' | '.join([this_artist['name'] for this_artist in track['artists']])],
                             acousticness=[this_feature['acousticness']],
                             analysis_url=[this_feature['analysis_url']],
                             danceability=[this_feature['danceability']],
                             duration_ms=[this_feature['duration_ms']],
                             energy=[this_feature['energy']],
                             instrumentalness=[this_feature['instrumentalness']],
                             key=[this_feature['key']],
                             liveness=[this_feature['liveness']],
                             loudness=[this_feature['loudness']],
                             mode=[this_feature['mode']],
                             speechiness=[this_feature['speechiness']],
                             tempo=[this_feature['tempo']],
                             time_signature=[this_feature['time_signature']],
                             track_href=[this_feature['track_href']],
                             type=[this_feature['type']],
                             uri=[this_feature['uri']],
                             valence=[this_feature['valence']],
                             popularity=[track['popularity']],
                             reason_added=[reason])
    return f_temp


####################################################
#           INITIALIZE TOKENS
####################################################
scope1 = 'user-library-read'
token1 = util.prompt_for_user_token(username,scope1,
                           client_id='75eb53595b114474a60c1eb521c81c5d',
                           client_secret='e5b3497fd13a45c59a18489b18454194',
                           redirect_uri='http://localhost/')

scope2 = 'user-top-read'
token2 = util.prompt_for_user_token(username,scope2,
                                   client_id='75eb53595b114474a60c1eb521c81c5d',
                                   client_secret='e5b3497fd13a45c59a18489b18454194',
                                   redirect_uri='http://localhost/')


scope3 = 'user-follow-read'
token3 = util.prompt_for_user_token(username,scope3,
                                   client_id='75eb53595b114474a60c1eb521c81c5d',
                                   client_secret='e5b3497fd13a45c59a18489b18454194',
                                   redirect_uri='http://localhost/')


scope4 = 'playlist-modify-public'
token4 = util.prompt_for_user_token(username,scope4,
                                   client_id='75eb53595b114474a60c1eb521c81c5d',
                                   client_secret='e5b3497fd13a45c59a18489b18454194',
                                   redirect_uri='http://localhost/')


df_my_tracking_artists = pd.DataFrame(data = new_artist_entry())
df_track_features = pd.DataFrame(data = new_track_entry())

####################################################
# task 1: my favourite artists from saved songs and PUBLIC playlists
####################################################
print("\nStep1: get artists from my saved songs and public playlists")
if token1:
    sp = spotipy.Spotify(auth=token1)
    results = sp.current_user_saved_tracks(limit = 50)
    n_offset = 0
    counter = 0
    while len(results['items']) > 0:
        for this_item in results['items']:
            counter += 1
            track = this_item['track']
            d_temp = artist_entry_from_track(track, playlist_name = 'saved songs')
            df_my_tracking_artists = df_my_tracking_artists.append(pd.DataFrame(data=d_temp)) 
            
            if track['uri'] not in df_track_features['uri'].tolist():
                this_feature = sp.audio_features(track['uri'])[0]
                f_temp = track_entry(track = track, this_feature = this_feature, reason = 'saved songs')
                df_track_features = df_track_features.append(pd.DataFrame(data=f_temp)) 
            
        n_offset += 50
        print("... getting next 50 items ...")
        results = sp.current_user_saved_tracks(limit = 50, offset = n_offset)    
        
    print('{} items processed. Now: total_artists = {}, total_tracks = {}'.format(
            counter, len(df_my_tracking_artists), len(df_track_features)))

    # public playlists
    playlists = sp.user_playlists(username)
    ID_playlist = []
    name_playlist = []
    while playlists:
        for i, playlist in enumerate(playlists['items']):
            if playlist['owner']['id'] == username and 'my new release' not in playlist['name']:
                ID_playlist += [playlist['id']]
                name_playlist += [playlist['name']]
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None
            
    print("Going to process {} PUBLIC playlists ... ".format(len(ID_playlist)))
        
    for i in range(len(ID_playlist)):
        this_playlist = ID_playlist[i]
        this_playlist_name = name_playlist[i]
        if this_playlist_name == "my new release":
            continue
        pl_details = sp.user_playlist_tracks(username, this_playlist)
        counter_existing_artist = len(df_my_tracking_artists)
        counter_track = 0
        for this_item in pl_details['items']:
            track = this_item['track']
            
            d_temp = artist_entry_from_track(track, playlist_name = this_playlist_name)
            df_my_tracking_artists = df_my_tracking_artists.append(pd.DataFrame(data=d_temp)) 
            
            if track['uri'] not in df_track_features['uri'].tolist():
                counter_track += 1
                this_feature = sp.audio_features(track['uri'])[0]
                f_temp = track_entry(track = track, this_feature = this_feature, 
                                     reason = 'playlist ' + this_playlist_name)
                df_track_features = df_track_features.append(pd.DataFrame(data=f_temp)) 
            
        print('Playlist {} processed. Total {} new tracks, {} new artists; now total {} artists'.format(
                this_playlist_name, counter_track, len(df_my_tracking_artists) - counter_existing_artist, len(df_my_tracking_artists)))
        
else:
    print ("Can't get token for", username)
    
print('Now: total_artists = {}, total_tracks = {}'.format(
            len(df_my_tracking_artists), len(df_track_features)))
    
####################################################
# task 2: get my top artists and top tracks (short term to long term)
####################################################
print("\nStep2: get artists from my top songs and top artists")
if token2:
    sp = spotipy.Spotify(auth=token2)
    # top artists
    for term in [ 'short_term', 'medium_term', 'long_term']:
        this_top_50 = sp.current_user_top_artists(limit = 50, time_range = term)
        print('\nMy Top 10 artists for {}'.format(term))
        for i in range(50):
            this_artist = this_top_50['items'][i]            
            d_temp = artist_entry_from_artist(artist = this_artist, 
                                              playlist_name='top artist' + term,
                                              track_name='')            
            df_my_tracking_artists = df_my_tracking_artists.append(pd.DataFrame(data=d_temp))     
            
            if i<50:
                print('     no.{:2d}: {:25s}, FOLLOWERS {:8d}, GENRES: {}'.format(i+1, 
                      this_artist['name'], 
                      this_artist['followers']['total'], 
                      format_genres(this_artist['genres'])))
            
            
    for term in [ 'short_term', 'medium_term', 'long_term']:
        this_top_50 = sp.current_user_top_tracks(limit = 50, time_range = term)
        print('\nMy Top 10 played tracks for {}'.format(term))
        for i in range(50):
            track = this_top_50['items'][i]
            d_temp = artist_entry_from_track(track, playlist_name = 'top track ' + str(i+1)+ ' ' + term)
            df_my_tracking_artists = df_my_tracking_artists.append(pd.DataFrame(data=d_temp)) 
            
            if track['uri'] not in df_track_features['uri'].tolist():
                this_feature = sp.audio_features(track['uri'])[0]
                f_temp = track_entry(track = track, this_feature = this_feature, reason = 'top songs ' + term)
                df_track_features = df_track_features.append(pd.DataFrame(data=f_temp)) 
            
            if i<50:
                print('     no.{:2d}: {:35s}, ARTIST {:20s}, release date: {:10s} , explicit ?: {}'.format(i+1, 
                      track['name'], 
                      track['artists'][0]['name'], 
                      track['album']['release_date'],
                      track['explicit']))            
            
else:
    print ("Can't get token for", username)
    

if token3:
    sp = spotipy.Spotify(auth=token3)
    results = sp.current_user_followed_artists(limit = 50)['artists']['items']
    while len(results) > 0:        
        for this_artist in results:
            d_temp = artist_entry_from_artist(artist = this_artist, 
                                  playlist_name='following',
                                  track_name='')   
            df_my_tracking_artists = df_my_tracking_artists.append(pd.DataFrame(data=d_temp))       
            
        results = sp.current_user_followed_artists(limit = 50, after = this_artist)['artists']['items']    
print('Now: total_artists = {}, total_tracks = {}'.format(len(df_my_tracking_artists), len(df_track_features)))    
    
####################################################
# task 3: finalize artists list
####################################################
# pooled artists
artists_summary = pd.pivot_table(df_my_tracking_artists, values = ['playlist'], index = ['id','name','uri'], aggfunc ='count')
artists_summary = artists_summary.sort_values('playlist', ascending=False)
artists_summary = artists_summary.reset_index()
# keep only when: pop not in, unless it is also metal....
final_IDs = []
related_artists_IDs = []
my_genres = []
dict_artist_genre = {}
dict_genre_artist = {}
artists_w_unknown_genres = []
for this_id in artists_summary.loc[:,'id']:
    info_artist = sp.artist(this_id)
    skip_this_artist = False
    
    if len(info_artist['genres']) == 0:
        skip_this_artist = True # dont know what...
        artists_w_unknown_genres += [info_artist['name']]
        
    # handling of genres of artists
    for this_artist_genre in info_artist['genres']:
        for this_exclude_keyword in genres_to_exclude:
            if this_artist_genre.lower() in this_exclude_keyword.lower() or this_exclude_keyword.lower() in this_artist_genre.lower():
                skip_this_artist = True # any word intersect, EXCLUDE
        for this_reinclude_keyword in genres_to_reinclude:
            if this_artist_genre.lower() in this_reinclude_keyword.lower() or this_reinclude_keyword.lower() in this_artist_genre.lower():
                skip_this_artist = False # any word intersect, RE-INCLUDE
            
    if info_artist['name'] in must_include_artists:
        skip_this_artist = False  
            
    if not skip_this_artist:
        final_IDs.append(this_id)    
        related_artists_list = sp.artist_related_artists(this_id)['artists']    
        related_artists_IDs.extend([x['id'] for x in related_artists_list])
        my_genres.extend(info_artist['genres'])
        dict_artist_genre[info_artist['name']] = info_artist['genres']
        for i_genre in info_artist['genres']:
            if i_genre not in dict_genre_artist.keys():
                dict_genre_artist[i_genre] = []
            dict_genre_artist[i_genre].append(info_artist['name'])
            
            
c = Counter(related_artists_IDs)   
for key,value in c.items():
    if value >= threshold_related:
        final_IDs.append(key)    

final_IDs = list(set(final_IDs))
my_genres = list(set(my_genres)) 
genre_ranker = pd.DataFrame(columns = ['n_artists','list_artists'])            
for this_genre in dict_genre_artist.keys():
    this_list = dict_genre_artist[this_genre]
    genre_ranker.loc[this_genre] = [len(this_list), ' | '.join(this_list)]

genre_ranker.sort_values(['n_artists'], ascending = False)

if create_genre_csv:
    genre_ranker.to_csv('genre_ranker_{}.csv'.format(datetime.datetime.today().isoformat()[:10]), index = False)
if create_track_csv:
    df_track_features.to_csv('track_feature.csv', index = False)

if len(artists_w_unknown_genres) > 0:
    print("Missing genre information for them, include in config if desired: {}".format(
            [s for s in artists_w_unknown_genres if s not in must_include_artists]
            ))


##############################################################
# task 4: Now, get the NEW RELEASE for these final artists!!!!
##############################################################
playlist_name = "my new release - " + datetime.datetime.today().isoformat()[:10]
playlist_description = "Playlist generated by my own python script, using Spotipy at https://github.com/plamere/spotipy"

print("About to create a public playlist named = '{}'\n, description = '{}'")
response = input("Type YES to continue:")
if response == "YES":
    list_artist_track = []
    if token4:
        sp = spotipy.Spotify(auth=token4)
        
        playlists = sp.user_playlist_create(username, playlist_name,
                                            public = True, description = playlist_description)     
        target_playlist = playlists['id']
        existing_tracks = [ x['track']['id'] for x in sp.user_playlist_tracks(username, target_playlist)['items']]
        
        i = 0
        for this_id in final_IDs[i:]:
            # albums
            albums = sp.artist_albums(this_id)['items']   
            for album in albums:
                if len(album['release_date'])==10:
                # Assumption here: I dont care about album with 'invalid' date, must be ancient
                    if album['release_date'] >= start_search_date:
                        # This album is CHOSEN!
                        for track in sp.album_tracks(album['id'])['items']:
                            skip = False
                            for key_word in key_words_exclude_trackname:
                                if key_word in track['name'].lower():
                                    skip = True   
                            if track['id'] in existing_tracks:
                                skip = True
                            artists_this_track = [this_artist['id'] for this_artist in track['artists']]
                            if (this_id in artists_this_track) and (not skip):
                                if (this_id+'---'+track['name']) not in list_artist_track:
                                    # This track is chosen
                                    sp.user_playlist_add_tracks(user=username, playlist_id=target_playlist,tracks=[track['id']])
                                    print('{},  {}, {:35s}, ARTIST {:20s}'.format(i,
                                          track['id'], track['name'], 
                                          track['artists'][0]['name']))  
                                    list_artist_track.append(this_id+'---'+track['name']) 
            i += 1                        

    
