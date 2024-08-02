# the-Philbott
Our church puts the pastor's messages on Youtube each week.  I wanted to make those uploads a little more marketable with AI!

## What you get in this repo
This is a script that, in conjunction with a [vosk](https://github.com/alphacep/vosk-api/) model, will accept a video file and provide the following:

- A Transcript of the video
- A Clickbait Title based on the themes in the transcript
- A list of suggested hashtags to apply to your upload
- A 4-8 sentence summary suitable for a youtube description field
- A list of 'quotable moments' in the video
- Clips of the video containing those quotable moments in a 25-second file suitable for a tiktok/reel type upload
- A list of discussion questions about the content

## What it's made of

- [Vosk](https://github.com/alphacep/vosk-api/) provides the ability to transcribe from a mp4.
- [Ollama](https://www.ollama.com) provides a LLM to process the transcript and prompt it to create/identify content.
- [Chroma](https://trychroma.com) provides in-memory vector db for embeddings so that Ollama can process the transcript.

## How to use this code

1. Download a model from [Vosk](https://alphacephei.com/vosk/models).  The code currently uses `vosk-model-en-us-0.42-gigaspeech` but you can change that by changing the `MODEL_FOLDER` variable in `transcripter.py`.  **Transcripter is expecting the vosk folder to be in the same folder as main.py.**

2. Set up your venv.  In your terminal, run:

```bash
python -m venv .venv
source .venv/bin/activate #in Windows, source .venv/Scripts/activate
```

You should have a little decorator before your command prompt now that looks like `(.venv)`.  Note - every time you run the application, you need to ensure this appears, or things won't work right!

3. Install dependencies.  In your terminal, run

```bash
pip install -r requirements.txt
```

4. Install [ffmpeg](https://ffmpeg.org/download.html), which is used for extracting the audio from the video file as well as cutting the short-form clips.  Follow whatever standard installation instructions are for your platform - if you can run `ffmpeg -version` from your command line and not get an error message, you're ready to go on to the next step.

5. Install [Ollama](https://ollama.com).

6. From a command prompt, run the following:

`ollama pull llama3.1`

(You can of course swap out llama3.1 with any other LLM that you like, as long as Ollama uses `localhost:11434` to provide an interface to it.)

This will cause Ollama to run a background process on your machine with the Llama3.1 model listening for inputs from the program.  **Ollama *must* be running for the Philbott to work!** . You can verify this by pointing your web browser to `https://localhost:11434`. If you get a message that Ollama is running, you're good to go to the next step.

## How to run the Philbott

### The Config File
`config.yaml` is how you define what prompts are used by the system to create your outputs.  The opening of a config is ALWAYS defining the list of 'prompts' as follows:

```yaml
prompts:
```

Beneath this 'prompts' label is a repeating list of individual configuration values.  Yaml starts each entry with a hyphen and then lists the name/value pairs, one on each line.

The first entry in every prompt is its 'type'.We currently support the following types:

| Type | Description |
|---|---|
| SimpleText | This is a prompt that will return text from the LLM.  It's a Q&A, or summary, or similar conversation where the response is always text that we use for something.
| VideoClipArray | This is a prompt that returns a pipe (`\|`) delimited list of inputs to be passed to our video-clip finder.  This can be used for cases like "find a quotable moment" or "locate the point where a key point was made".  You can match up the count of elements.  Your prompt will be modified to request the pipe-delimited output format before being sent to the LLM.


### Kicking off the process
From your command prompt, you run:

```bash
python main.py 
  --file=path/to/your/video-file.mp4 
  --config=path/to/your/config.yaml
  --outputfolder=/path/to/destination/folder
```

> NOTE: the `outputfolder` parameter is optional - if you don't provide it, the Philbott will output its results to an "outputs" folder that it creates in the project folder.  If the folder already exists it will use it; if it does not exist, it will be created.  You can provide your path as absolute or relative by adding or omitting a leading '/' character... `/home/Ben/Documents` is an absolute path while `home/Ben/Documents` is relative to the current working directory.

The Philbott can take a while to process, depending on the size of your file!  A 30-minute video on a Macbook M2 ran for about 2 minutes.

When it's complete, you'll have a series of new .txt files in the project root as well as some 25-second-long mp4s.