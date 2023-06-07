import soundfile as sf
import torch
import torchaudio
import os
import argparse
import torch
import librosa
import time
from scipy.io.wavfile import write
from tqdm import tqdm
import numpy as np

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

def speech_and_silence(audio_path,save_temp_path,music_name):

  # get the vad model and utils
  model_and_utils = get_vad_model_and_utils(use_cuda=False)

  # get the speech timestamps
  speech_frames = return_speech_segments(model_and_utils, audio_path, vad_sample_rate=8000, use_cuda=False)

  # get the sampling rate of original audio
  _ , sr_audio_original = read_audio(audio_path)

  # load the original audio
  wav_src_all, _ = librosa.load(audio_path, sr=sr_audio_original)

  if not speech_frames:
      speech_frames = [{"start":0, "end":len(wav_src_all)-1}]

  slice_audios = []
  for i in range(len(speech_frames)):
      try:
          start = speech_frames[i]["start"]
          end = speech_frames[i]["end"]
          wav_src = wav_src_all[start:end]

          slice_audios.append(wav_src_all[speech_frames[i]["start"] - 4000 : speech_frames[i]["end"] + 4000])

      except Exception as e:
          print(e)
          slice_audios.append(np.zeros(wav_src_all[start:end].shape))

  for i in range(len(slice_audios)):
    segmented_audio = slice_audios[i]
    write(save_temp_path + '/' + music_name + '_' + str(i) + '.wav', sr_audio_original, segmented_audio) # save all segments in path
  
  return slice_audios # return a list with all segments

def concatenate_segments(segments,save_path,sr_audio,file_name):
  #concatenate segments
  audio = np.concatenate(segments)
  #save full audio
  write(save_path + '/' + file_name + 'full_audio' + '.wav' , sr_audio, audio)
  print("All audio is saved at:", save_path)
  return audio

def sr_conversion(input_filepath,output_filepath,target_sr):

    waveform, sr = librosa.load(input_filepath, sr=None)
    print(sr)
    target_waveform = librosa.resample(waveform, orig_sr=sr, target_sr=target_sr)
    sf.write(output_filepath, target_waveform, target_sr, format='wav')
    print(f'SAMPLING RATE CHANGED TO {target_sr}')