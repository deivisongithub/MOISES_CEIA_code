path = input('save path: ')             #/content/gdrive/MyDrive/TEST BASE/download_music_youtube/musicas_baixadas
playlist_url = input('playlist link: ') #'https://www.youtube.com/playlist?list=PLE3qmK9SMKaj7vNOQ1nWWu8wC-sfwdm_k'

import sys
sys.path.insert(1,path)
import os
import subprocess
import re
from pytube import YouTube
from pytube import Playlist

play = Playlist(playlist_url)

play._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")
print(len(play.video_urls))


for url in play.video_urls:
    yt = YouTube(url)
    audio = yt.streams.get_audio_only() #get only the audio
    audio.download(path)                # download the audio
    nome = yt.title
    new_filename=nome+'.m4a'
    default_filename =nome+'.mp4'
    print(new_filename)
    
    os.environ['inputFile'] = path + "/" + default_filename
    os.environ['outputPath'] = path
    os.environ['fileName'] = new_filename

print('== Download Completo ==')