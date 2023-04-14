import soundfile as sf
import torch
import torchaudio

def read_audio(path):
    wav, sr = torchaudio.load(path)

    if wav.size(0) > 1:
        wav = wav.mean(dim=0, keepdim=True)

    return wav.squeeze(0), sr


def resample_wav(wav, sr, new_sr):
    wav = wav.unsqueeze(0)
    transform = torchaudio.transforms.Resample(orig_freq=sr, new_freq=new_sr)
    wav = transform(wav)
    return wav.squeeze(0)


def map_timestamps_to_new_sr(vad_sr, new_sr, timestamps, just_begging_end=False):
    factor = new_sr / vad_sr
    new_timestamps = []
    for ts in timestamps:
        # map to the new SR
        new_dict = {"start": int(ts["start"] * factor), "end": int(ts["end"] * factor)}
        new_timestamps.append(new_dict)

    return new_timestamps


def get_vad_model_and_utils(use_cuda=False):
    model, utils = torch.hub.load(repo_or_dir="snakers4/silero-vad", model="silero_vad", force_reload=True, onnx=False)
    if use_cuda:
        model = model.cuda()

    get_speech_timestamps, save_audio, _, _, collect_chunks = utils
    return model, get_speech_timestamps, save_audio, collect_chunks


def return_speech_segments(
    model_and_utils, audio_path, vad_sample_rate=8000, use_cuda=False
):
    # get the VAD model and utils functions
    model, get_speech_timestamps, _, _ = model_and_utils

    # read ground truth wav and resample the audio for the VAD
    wav, gt_sample_rate = read_audio(audio_path)

    # if needed, resample the audio for the VAD model
    if gt_sample_rate != vad_sample_rate:
        wav_vad = resample_wav(wav, gt_sample_rate, vad_sample_rate)
    else:
        wav_vad = wav

    if use_cuda:
        wav_vad = wav_vad.cuda()

    # get speech timestamps from full audio file
    speech_timestamps = get_speech_timestamps(wav_vad, model, sampling_rate=vad_sample_rate, window_size_samples=768)

    # map the current speech_timestamps to the sample rate of the ground truth audio
    new_speech_timestamps = map_timestamps_to_new_sr(
        vad_sample_rate, gt_sample_rate, speech_timestamps
    )
    return new_speech_timestamps

import os
import argparse
import torch
import librosa
import time
from scipy.io.wavfile import write
from tqdm import tqdm
import numpy as np

def speech_and_silence(audio_path,save_temp_path):

  model_and_utils = get_vad_model_and_utils(use_cuda=False)
  speech_frames = return_speech_segments(model_and_utils, audio_path, vad_sample_rate=8000, use_cuda=False)

  _ , sr_audio_original = read_audio(audio_path)

  wav_src_all, _ = librosa.load(audio_path, sr=sr_audio_original)

  if not speech_frames:
      speech_frames = [{"start":0, "end":len(wav_src_all)-1}]

  slice_audios = []
  for i in range(len(speech_frames)):
      try:
          start = speech_frames[i]["start"]
          end = speech_frames[i]["end"]
          wav_src = wav_src_all[start:end]

          if i == 0:
              if start != 0:
                  slice_audios.append(wav_src_all[: speech_frames[i+1]["start"]])
          else: # normal samples

              if i != len(speech_frames)-1:
                  next_start = speech_frames[i+1]["start"]
                  slice_audios.append(wav_src_all[start:next_start])
              else:
                slice_audios.append(wav_src_all[start:])

      except Exception as e:
          print(e)
          slice_audios.append(np.zeros(wav_src_all[start:end].shape))

  for i in range(len(slice_audios)):
    segmented_audio = slice_audios[i]
    write(save_temp_path + '/' + 'segment_' + str(i) + '.wav', sr_audio_original, segmented_audio)
  
  return slice_audios

def concatenate_segments(segments,save_path,sr_audio):
    audio = np.concatenate(segments)
    write(save_path + '/' + 'full_audio' + '.wav' , sr_audio, audio)
    print("All audio is saved at:", save_path)
    return audio

audio_path = input('wav file path: ')                   #/content/drive/MyDrive/music_segments/input/Coldplay_Paradise.wav
save_segments_path = input('save segments path: ')      #/content/drive/MyDrive/music_segments/output
save_path = input('save path: ')                        #/content/drive/MyDrive/music_segments/output

_ , sr_audio = read_audio(audio_path)
segments = speech_and_silence(audio_path,save_segments_path)
full_audio = concatenate_segments(segments,save_path,sr_audio)