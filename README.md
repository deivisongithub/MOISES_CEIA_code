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

## Dependencies

This script requires the following libraries:

- appdirs==1.4.4
- audioread==3.0.0
- certifi==2023.5.7
- cffi==1.15.1
- charset-normalizer==3.1.0
- colorama==0.4.6
- decorator==5.1.1
- dropbox==11.36.0
- filelock==3.12.0
- idna==3.4
- Jinja2==3.1.2
- joblib==1.2.0
- lazy_loader==0.2
- librosa==0.10.0.post2
- llvmlite==0.40.0
- MarkupSafe==2.1.2
- mpmath==1.3.0
- msgpack==1.0.5
- networkx==3.1
- numba==0.57.0
- numpy==1.24.3
- packaging==23.1
- ply==3.11
- pooch==1.6.0
- pycparser==2.21
- pytube==15.0.0
- PyYAML==6.0
- requests==2.30.0
- scikit-learn==1.2.2
- scipy==1.10.1
- six==1.16.0
- soundfile==0.12.1
- soxr==0.3.5
- stone==3.3.1
- sympy==1.12
- threadpoolctl==3.1.0
- torch==2.0.1
- torchaudio==2.0.2
- tqdm==4.65.0
- typing_extensions==4.5.0
- urllib3==2.0.2

## Install 

To install dependencies, run the command:

```bash
$ pip install -r requirements.txt
```

## How to use

To execute the audio processing pipeline, run the following command:

```bash
$ python main.py
```
After that just give the required parameters in the terminal:

```bash
Video Link: 
output path: 
```
Example:
```bash
Video Link: https://www.youtube.com/watch?v=ZEcqHA7dbwM
output path: C:\Users\Deivison\Desktop\MOISES\pipeline\output
```

Output Example:
![outoutexample](https://github.com/deivisongithub/MOISES_CEIA_code/assets/81170028/d2e27396-6b91-41e9-a845-957dfa1c6661)
