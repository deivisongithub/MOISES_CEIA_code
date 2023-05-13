# Changer Singer

This python script executes an audio processing pipeline to change singer of songs.

The script consists of several audio processing steps including:

- Download music audio from youtube
- Isolate voice and instrumentals
- Segments the vocal into smaller chunks
- Change the singer
- Concatenates segments with changed singer
- Mix the new voice and instrumental

The pipeline is executed for each music folder within the specified input directory. The specified output directory will contain the normalized files for each music.

## Dependencies

This script requires the following libraries:

- torch==2.0.0
- torchaudio==2.0.1
- webrtcvad==2.0.10
- pydub==0.25.1
- librosa==0.10.0
- tqdm==4.65.0

## Install 

I recommend using a virtual conda environment:

```bash
$ conda create -n moises python=3.9 pip
$ conda activate moises
```

To install dependencies, run the command:

```bash
$ sudo apt-get update; sudo apt-get install ffmpeg
```
And install the requirements:

```bash
$ pip install -r requirements.txt
```

## How to use

To execute the audio processing pipeline, run the following command:

```bash
$ python main.py --input=input_folder --output=output_folder
```
