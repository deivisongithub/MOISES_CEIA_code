from pydub import AudioSegment
from pydub.utils import mediainfo
from download_audio_youtube import download_music_youtube
from request_api_moises import *
from music_segments_speech_silence import *
import json
import ffmpeg

do_segment = input('--do_segment[True/False]: ')
do_concatenate = input('--do_concatenate[True/False]: ')

if do_segment == 'True':
    do_concatenate = 'False'


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
    Youtube_music_path = os.path.join(output_path, 'youtube_music')
    timestamps_path = os.path.join(output_path, 'timestamps')

    # make the directorys
    path_list = [Youtube_music_path, isolated_voice_path,
                 isolated_background_path, segments_path, timestamps_path]

    for folder in path_list:
        if os.path.isdir(folder):
            print('---this directory already exists---')
        else:
            os.mkdir(folder)

    # download the audio of youtube video
    print('starting download...')
    # get file name
    filename = download_music_youtube(LINK_VIDEO, Youtube_music_path)

    # isolate the voice and background

    Youtube_music_path_m4a = os.path.join(
        Youtube_music_path, filename + '.m4a')
    print(Youtube_music_path_m4a)
    Youtube_music_path_wav = Youtube_music_path + "/" + filename + '.wav'
    print(Youtube_music_path_wav)

    # m4a to wav
    sound = AudioSegment.from_file(Youtube_music_path_m4a)
    sound.export(Youtube_music_path_wav, format="wav")

    os.remove(Youtube_music_path_m4a)

    # change SR to 16K
    sr_conversion(Youtube_music_path_wav,
                  Youtube_music_path_wav, SAMPLING_RATE)

    url, path = dropbox_generator(
        Youtube_music_path_wav, DROPBOX_PATH)
    print(url)

    json_file = moises_isolate_voice(filename, url, KEY_ORCHES)
    # print(json_file)

    delete_dropbox(path, DROPBOX_PATH)

    # downloading and storing isolated voice and background
    print('Download files...')
    file_url = json_file['Output 1']
    file_url2 = json_file['Output 2']

    file = os.path.join(isolated_voice_path, filename + '.wav')
    file2 = os.path.join(isolated_background_path,
                         filename + '_background' + '.wav')

    request.urlretrieve(file_url, file)
    request.urlretrieve(file_url2, file2)

    # change output moises api SR to 16K
    sr_conversion(file, file, SAMPLING_RATE)

    # Make voice segments
    audio_path = os.path.join(isolated_voice_path, filename + '.wav')
    print('making the segments...')

    _, sr_audio = read_audio(audio_path)  # get sampling rate

    #change filename
    filename = 'segment'

    segments, timestamps, n_segments = speech_and_silence(
        audio_path, segments_path, filename)

    dict_timestamps = {'timestamps': timestamps,
                       'num_segments': n_segments, 'file_name': filename}

    # make a json with timestamps and number of segments
    with open(timestamps_path + '/' + filename + '.json', 'w') as fp:
        json.dump(dict_timestamps, fp)


if do_concatenate == 'True':

    # input
    modified_segments_path = input('modified segments path: ')
    isolated_background_wav = input('isolated background .wav: ')
    timestamps_json = input('timestamps .json: ')

    # get timestamps
    with open(timestamps_json, 'r') as fp:
        data = json.load(fp)

    # Get name of song

    # filename = data['file_name']
    filename = 'segment'

    # Get the segments
    timestamps = data['timestamps']
    n_segments = data['num_segments']

    # verify and change SAMPLE RATE
    for i in range(n_segments):
        # take path
        _, sr_segment = read_audio(
            modified_segments_path + '/' + filename + '_' + str(i) + '.wav')

        # verify and change Sample rate
        if sr_segment != SAMPLING_RATE:
            segments_path_current = modified_segments_path + \
                '/' + filename + '_' + str(i) + '.wav'
            sr_conversion(segments_path_current,
                          segments_path_current, SAMPLING_RATE)

    # change sr of background
    _, sr_bg = read_audio(isolated_background_wav)
    if sr_bg != SAMPLING_RATE:
        sr_conversion(isolated_background_wav,
                      isolated_background_wav, SAMPLING_RATE)

    # verify and change BIT RATE

    # make the directory aux
    new_br_path = modified_segments_path + '/' + 'new_br'
    if os.path.isdir(new_br_path):
        print('---this directory already exists---')
    else:
        os.mkdir(new_br_path)

    # take min biterate
    min_bitrate = [int(mediainfo(modified_segments_path + '/' + filename +
                       '_' + str(i) + '.wav')['bit_rate']) for i in range(n_segments)]
    min_bitrate.append(int(mediainfo(isolated_background_wav)['bit_rate']))
    min_bitrate = min(min_bitrate)//1000

    # change bitrate of segments
    for i in range(n_segments):

        segments_path_current = modified_segments_path + \
            '/' + filename + '_' + str(i) + '.wav'

        stream = ffmpeg.input(segments_path_current)
        stream = ffmpeg.output(stream, new_br_path + '/' + filename +
                               '_' + str(i) + '.wav', bitrate=str(min_bitrate) + 'k')
        ffmpeg.run(stream)

    # change bitrate of background

    # make the directory aux
    new_br_bg_path = output_path + '/' + 'isolated_background' + '/' + 'new_br'
    if os.path.isdir(new_br_bg_path):
        print('---this directory already exists---')
    else:
        os.mkdir(new_br_bg_path)

    audio_background_path = new_br_bg_path + '/' + 'isolate_voice' + '.wav'

    stream = ffmpeg.input(isolated_background_wav)
    stream = ffmpeg.output(stream, audio_background_path,
                           bitrate=str(min_bitrate) + 'k')
    ffmpeg.run(stream)

    # concatenate segments
    concatene_list = []
    for i in range(n_segments):

        if i == 0:
            try:
                # add silence
                concatene_list.append(np.zeros(timestamps[i]['start'] - 1))

                # take path
                speech_segment, sr_segment = read_audio(
                    new_br_path + '/' + filename + '_' + str(i) + '.wav')

                # add voice
                concatene_list.append(speech_segment)

                # add silence
                concatene_list.append(
                    np.zeros(timestamps[i+1]['start'] - timestamps[i]['end']))

            except:
                # take path
                speech_segment, sr_segment = read_audio(
                    new_br_path + '/' + filename + '_' + str(i) + '.wav')

                # add voice
                concatene_list.append(speech_segment)

                # add silence
                concatene_list.append(
                    np.zeros(timestamps[i+1]['start'] - timestamps[i]['end']))

            continue

        else:
            if i < n_segments - 1:
                # take path
                speech_segment, sr_segment = read_audio(
                    new_br_path + '/' + filename + '_' + str(i) + '.wav')

                # add voice
                concatene_list.append(speech_segment)

                # add silence
                concatene_list.append(
                    np.zeros(timestamps[i+1]['start'] - timestamps[i]['end']))

            else:
                # take path
                speech_segment, sr_segment = read_audio(
                    new_br_path + '/' + filename + '_' + str(i) + '.wav')

                # add voice
                concatene_list.append(speech_segment)

    # Set the directory path
    concatenate_segments_path = os.path.join(
        output_path, 'concatenate_segments')
    new_speaker_path = os.path.join(output_path, 'new_speaker')

    # make the directorys
    path_list = [concatenate_segments_path, new_speaker_path]

    for folder in path_list:
        if os.path.isdir(folder):
            print('---this directory already exists---')
        else:
            os.mkdir(folder)

    # Concatenate segments
    full_audio = concatenate_segments(
        concatene_list, concatenate_segments_path, SAMPLING_RATE, filename)

    # mixer voice and background

    new_voice_path = os.path.join(
        concatenate_segments_path, filename + 'full_audio' + '.wav')
    print(new_voice_path)

    # mixer audios
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
