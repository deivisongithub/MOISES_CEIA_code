import shutil
from pytube import YouTube
import os

def download_music_youtube(VIDEO_URL,path):

  yt = YouTube(VIDEO_URL)

  audio = yt.streams.filter(only_audio=True)[0]
  audio.download(path)

  name = yt.title
  new_filename= name+'.m4a'
  default_filename = name+'.mp4'
  print(new_filename)

  shutil.move(os.path.join(path,default_filename),os.path.join(path, new_filename))

  print('== Download Completo ==')

  return name