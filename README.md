# Changer Singer

This python script executes an audio processing pipeline to change singer of songs.

The script consists of several audio processing steps including:

- Download music audio from youtube
- Isolate voice and instrumentals
- Segments the vocal into smaller chunks
- Change the singer
- Concatenates segments with changed singer
- Mix the new voice and instrumental

The pipeline is executed for the given Youtube link and the specified output directory will contain the audio files at each step of the process.

## Install 

To install dependencies, run the command:

```bash
$ pip install -r requirements.txt
```

## How to use

It is very important that all .py and .yaml are in the same directory. 
available in:https://drive.google.com/file/d/1sWZJub-SbwnDXSFF5qSVfNsVIM9jAAxy/view?usp=share_link

To execute the audio processing pipeline, run the following command:

```bash
$ python main.py
```
After that just give the required parameters in the terminal,Example:

```bash
--do_segment[True/False]: True
--do_concatenate[True/False]: False
output path: C:\Users\Deivison\Desktop\MOISES\pipeline\output
```
In case, do_segment == 'TRUE':

provide the youtube link,Example:

```bash
Video Link: https://www.youtube.com/watch?v=ZEcqHA7dbwM
```
In case, do_concatenate == 'TRUE':

provide folders with segments and background .wav path,Example:

```bash
modified segments path: /home/deivison/Desktop/pipeline_final/output/segments
isolated background .wav: /home/deivison/MOISES_CEIA_code/output/isolated_background/Fly Me To The Moon_background.wav
timestamps .json: /home/deivison/MOISES_CEIA_code/output/timestamps/Fly Me To The Moon.json
```

Output Example:


![Screenshot from 2023-06-09 13-50-16](https://github.com/deivisongithub/MOISES_CEIA_code/assets/81170028/d226b566-1bde-4dff-a6f6-eab5fbd47e31)
