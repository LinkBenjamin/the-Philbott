# the-Philbott
Our church puts the pastor's messages on Youtube each week.  I wanted to make those uploads a little more marketable with AI!

## What you get in this repo
This is a script that, in conjunction with a [vosk](https://github.com/alphacep/vosk-api/) model, will accept a video file and provide the following:

- A Transcript of the video
- A Clickbait Title based on the themes in the transcript
- A 4-5 sentence summary suitable for a youtube description field.
- A list of 'quotable moments' in the video
- Clips of the video containing those quotable moments in a 45-second file suitable for a tiktok/reel type upload

## What it's made of

- [Vosk](https://github.com/alphacep/vosk-api/) provides the ability to transcribe from a mp4.
- [Ollama](https://www.ollama.com) provides a LLM to process the transcript and prompt it to create/identify content.
- [Chroma](https://trychroma.com) provides in-memory vector db for embeddings so that Ollama can process the transcript.

## How to use this code

1. Download a model from [Vosk](https://alphacephei.com/vosk/models).  The code currently uses `vosk-model-en-us-0.42-gigaspeech` but you can change that by changing the `MODEL_FOLDER` variable in `transcripter.py`.  I loaded the model folder into my project root directory.

2. Set up your venv:

```bash
python -m venv .venv
source .venv/bin/activate #in Windows, source .venv/Scripts/activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Install [ffmpeg](https://ffmpeg.org/download.html), which is used for extracting the audio from the video file as well as cutting the short-form clips.

## How to run the Philbott

From your command prompt, you run:

```bash
python main.py --file=path/to/your/video-file.mp4
```

> Note that it can take a while to process, depending on the size of your file!  A 30-minute video on a Macbook M2 ran for about 2 minutes.

When it's complete, you'll have a series of new .txt files in the project root as well as some 25-second-long mp4s.