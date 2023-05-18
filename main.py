from pydub import AudioSegment
from download_audio_youtube import download_music_youtube
from request_api_moises import *
from music_segments_speech_silence import *

do_segment = input('--do_segment[True/False]: ')
do_concatenate = input('--do_concatenate[True/False]: ')


KEY_ORCHES = "74240dc9-407d-44c7-83c4-4b8a489755d9"
DROPBOX_PATH = "dropbox.yaml"  # # .yaml credentials of a dropbox to upload inputs
SAMPLING_RATE = 16000

output_path = input('output path: ')

if do_segment == 'True':

    # input
    LINK_VIDEO = input('Video Link: ')

    # Set the directory path
    isolated_voice_path = os.path.join(output_path, 'isolated_voice')
    isolated_background_path = os.path.join(output_path, 'isolated_background')
    segments_path = os.path.join(output_path, 'segments')

    # make the directorys
    path_list = [isolated_voice_path, isolated_background_path, segments_path]

    for folder in path_list:
        try:
            os.mkdir(folder)
        except FileExistsError as e:
            print(f'The {folder} folder already exists')

    # download the audio of youtube video
    Youtube_music_path = os.path.join(output_path, 'youtube_music')
    print('starting download...')
    download_music_youtube(LINK_VIDEO, Youtube_music_path)

    # isolate the voice and background

    # Get all the files in the directory
    files = os.listdir(Youtube_music_path)

    for i in files:
        #get file name
        filename = os.path.splitext(i)[0]
        print(filename)

        Youtube_music_path_m4a = os.path.join(Youtube_music_path, i)
        print(Youtube_music_path_m4a)
        Youtube_music_path_wav = Youtube_music_path + "/" + filename + '.wav'
        print(Youtube_music_path_wav)

        #m4a to wav
        sound = AudioSegment.from_file(Youtube_music_path_m4a)
        sound.export(Youtube_music_path_wav, format="wav")

        os.remove(Youtube_music_path_m4a)

        #change SR
        Youtube_music_path_wav = Youtube_music_path + "/" + filename + '.wav'
        sr_conversion(Youtube_music_path_wav,Youtube_music_path_wav,SAMPLING_RATE)

        url, path = dropbox_generator(
            Youtube_music_path_wav, DROPBOX_PATH)
        print(url)

        json_file = moises_isolate_voice(filename, url, KEY_ORCHES)
        print(json_file)

        delete_dropbox(path, DROPBOX_PATH)

        # downloading and storing isolated voice and background
        print('Download files...')
        file_url = json_file['Output 1']
        file_url2 = json_file['Output 2']

        file = os.path.join(isolated_voice_path, filename + '.wav')
        file2 = os.path.join(isolated_background_path,filename + '_background' + '.wav')

        request.urlretrieve(file_url, file)
        request.urlretrieve(file_url2, file2)

    # Make voice + silence segments
    audio_path = os.listdir(isolated_voice_path)[0]
    audio_path = os.path.join(isolated_voice_path, audio_path)
    print('making the segments...')

    _, sr_audio = read_audio(audio_path)  # get sampling rate
    segments = speech_and_silence(audio_path, segments_path)


if do_concatenate == 'True':

    # input
    modified_segments_path = input('modified segments path: ')
    isolated_background_path = input('isolated background path: ')

    # Get the segments
    n_segments = len(os.listdir(modified_segments_path))
    modified_segments_list = [f'segment_{str(i)}.wav' for i in range(n_segments)]
    print(modified_segments_list)

    # get sampling rate
    _, sr_audio = read_audio(os.path.join(
        modified_segments_path, modified_segments_list[0]))

    segments = []

    for segment in modified_segments_list:
        audio_segment_temp, _ = read_audio(
            os.path.join(modified_segments_path, segment))
        segments.append(audio_segment_temp)

    # Get name of song

    filename = os.path.splitext(os.listdir(isolated_background_path)[0])[0]
    filename = filename.split('_')[0]

    # Set the directory path
    concatenate_segments_path = os.path.join(output_path, 'concatenate_segments')
    new_speaker_path = os.path.join(output_path, 'new_speaker')

    # make the directorys
    path_list = [concatenate_segments_path, new_speaker_path]

    for folder in path_list:
        try:
            os.mkdir(folder)
        except FileExistsError as e:
            print(f'The {folder} folder already exists')

    # Concatenate segments
    full_audio = concatenate_segments(
        segments, concatenate_segments_path, sr_audio, filename)

    # mixer voice and background

    new_voice_path = os.listdir(concatenate_segments_path)[0]
    new_voice_path = os.path.join(concatenate_segments_path, new_voice_path)
    print(new_voice_path)

    audio_background_path = os.listdir(isolated_background_path)[0]
    audio_background_path = os.path.join(isolated_background_path, audio_background_path)
    print(audio_background_path)

    #verify if are with same sr
    _,sr_concatenate = read_audio(new_voice_path)
    _,sr_background = read_audio(audio_background_path)

    if sr_concatenate != sr_background:

        sr_conversion(new_voice_path,new_voice_path,SAMPLING_RATE)
        sr_conversion(audio_background_path,audio_background_path,SAMPLING_RATE)
    
    #mixer audios
    print('mix audio...')
    url, path = dropbox_generator(new_voice_path, DROPBOX_PATH)
    print(url)

    url2, path2 = dropbox_generator(audio_background_path, DROPBOX_PATH)
    print(url2)

    json_file = moises_mixer_audios(url, url2, KEY_ORCHES)
    print(json_file)

    delete_dropbox(path, DROPBOX_PATH)
    delete_dropbox(path2, DROPBOX_PATH)

    # downloading and storing mixed audio
    print('download audio...')
    file_url = json_file

    file = os.path.join(new_speaker_path, filename + '.wav')

    request.urlretrieve(file_url, file)