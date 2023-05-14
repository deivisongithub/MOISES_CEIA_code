from download_audio_youtube import download_music_youtube
from request_api_moises import *
from music_segments_speech_silence import *

# input
LINK_VIDEO = input('Video Link: ')
output_path = input('output path: ')

# Set the directory path
isolated_voice_path = os.path.join(output_path,'isolated_voice')
isolated_background_path = os.path.join(output_path,'isolated_background')
segments_path = os.path.join(output_path,'segments')
concatenate_segments_path = os.path.join(output_path,'concatenate_segments')
new_speaker_path = os.path.join(output_path,'new_speaker')

# make the directorys
path_list = [isolated_voice_path,isolated_background_path,segments_path,concatenate_segments_path,new_speaker_path]

for folder in path_list:
    try:
        os.mkdir(folder)
    except FileExistsError as e:
        print(f'The {folder} folder already exists')

# download the audio of youtube video
Youtube_music_path = os.path.join(output_path,'youtube_music')
print('starting download...')
download_music_youtube(LINK_VIDEO,Youtube_music_path)

# isolate the voice and background
KEY_ORCHES = "74240dc9-407d-44c7-83c4-4b8a489755d9"
DROPBOX_PATH = "dropbox.yaml"  # # .yaml credentials of a dropbox to upload inputs

files = os.listdir(Youtube_music_path) # Get all the files in the directory

# Filter the files to only include those with a .m4a extension
mp4_files = [f for f in files if f.endswith('.m4a')]  # <- in case of another extension, change here.

for i in mp4_files:
    filename = os.path.splitext(i)[0]
    print(filename)

    url, path = dropbox_generator(Youtube_music_path + "/" + i,DROPBOX_PATH)
    print(url)

    json_file = moises_isolate_voice(filename, url, KEY_ORCHES)
    print(json_file)

    delete_dropbox(path,DROPBOX_PATH)

    # downloading and storing isolated voice and background

    file_url = json_file['Output 1']
    file_url2 = json_file['Output 2']

    file = os.path.join(isolated_voice_path, filename + '.wav')
    file2 = os.path.join(isolated_background_path, filename + '_background' + '.wav')

    request.urlretrieve(file_url, file)
    request.urlretrieve(file_url2, file2)

# Make voice + silence segments
audio_path = os.listdir(isolated_voice_path)[0]
audio_path = os.path.join(isolated_voice_path,audio_path)
print(audio_path)

_ , sr_audio = read_audio(audio_path) # get sampling rate
segments = speech_and_silence(audio_path,segments_path)


'''


DIOGO, YOUR CODE HERE
YOU CAN USE THE VARIABLE 'SEGMENTS' OR THE SEGMENTS SAVE IN FOLDER 'SEGMENTS'
CHANGE THE PARAMETRE 'segments' PER 'new speaker segments' OF NEXT FUNCTION 


'''
# Concatenate segments
full_audio = concatenate_segments(segments,concatenate_segments_path,sr_audio,filename)


#mixer voice and background

new_voice_path = os.listdir(concatenate_segments_path)[0]
new_voice_path = os.path.join(concatenate_segments_path,new_voice_path)
print(new_voice_path)

audio_background_path = os.listdir(isolated_background_path)[0]
audio_background_path = os.path.join(isolated_background_path,audio_background_path)
print(audio_background_path)

url, path = dropbox_generator(new_voice_path,DROPBOX_PATH)
print(url)

url2, path2 = dropbox_generator(audio_background_path,DROPBOX_PATH)
print(url2)

json_file = moises_mixer_audios(url, url2,KEY_ORCHES)
print(json_file)

delete_dropbox(path)
delete_dropbox(path2)

#downloading and storing mixed audio

file_url = json_file

file = os.path.join(new_speaker_path, filename + '.wav')

request.urlretrieve(file_url , file )