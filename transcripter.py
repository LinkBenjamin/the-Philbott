import os
import wave
import json
import subprocess
import string
from vosk import Model, KaldiRecognizer
from pydub import AudioSegment

MODEL_FOLDER = "vosk-model-en-us-0.42-gigaspeech"
AUDIO_FORMAT = "wav"
AUDIO_FILE = "audio.wav"
AUDIO_FILE_2 = "audio2.wav"
AUDIO_FRAME_RATE = 16000

class Transcripter():

    def __init__(self, inputFileName):
        self.file = inputFileName
        os.environ['VOSK_LOG_LEVEL'] = '0'  # Suppress Vosk logging
        self.model = Model(MODEL_FOLDER)
        self.transcript = ''
        self.timestamps = []  # Initialize an empty list to hold timestamps

    def getAudio(self):
        print("ffmpeg is extracting the audio.")
        subprocess.run(["ffmpeg", "-i", self.file, "-q:a", "0", "-map", "a", AUDIO_FILE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def transcribe(self):
        self.getAudio()
        
        # Convert audio file to desired format if needed
        audio = AudioSegment.from_file(AUDIO_FILE)
        audio = audio.set_frame_rate(AUDIO_FRAME_RATE).set_channels(1)
        print("Audio converted to mono")
        audio.export(AUDIO_FILE_2, format=AUDIO_FORMAT)
        
        # Initialize Vosk recognizer
        rec = KaldiRecognizer(self.model, AUDIO_FRAME_RATE)
        rec.SetWords(True)

        # Open the audio file
        wf = wave.open(AUDIO_FILE_2, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            print("Audio file must be WAV format mono PCM.")
            exit(1)

        # Print audio file properties for debugging
        print(f"Sample Rate: {wf.getframerate()}, Channels: {wf.getnchannels()}, Sample Width: {wf.getsampwidth()}, Compression Type: {wf.getcomptype()}")

        # Read and process the audio file in chunks
        results = []
        timestamps = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = rec.Result()
                print(f"Result: {result}")  # Print full result for debugging
                results.append(json.loads(result))
            else:
                partial_result = rec.PartialResult()

        # Get the final result and check its content
        final_result = rec.FinalResult()
        print(f"Raw Final Result: {final_result}")  # Print raw final result for debugging
        final_result_json = json.loads(final_result)
        print(f"Final Result JSON: {final_result_json}")

        # Add the final result to the results list if it's not empty
        if final_result_json:
            results.append(final_result_json)

        # Process all results to extract text and timestamps
        full_text = []
        for res in results:
            if 'text' in res:
                full_text.append(res['text'].strip())
            if 'result' in res:
                for word in res['result']:
                    word_tuple = (word['word'], word['start'], word['end'])
                    timestamps.append(word_tuple)
                    print(f"Word Tuple: {word_tuple}")

        # Close the audio file
        wf.close()

        # Clean up temporary files
        os.remove(AUDIO_FILE)
        os.remove(AUDIO_FILE_2)

        # Store the full transcript and timestamps
        self.transcript = ' '.join(full_text)
        self.timestamps = timestamps

        return self.transcript
    
    def getTimestamps(self):
        return self.timestamps

    def findStringTimestamps(self, search_string):
        # Function to normalize text (lowercase and remove punctuation)
        def normalize(text):
            return text.lower().translate(str.maketrans("", "", string.punctuation))

        # Normalize the search string
        normalized_search_words = [normalize(word) for word in search_string.split()]

        # Extract and normalize words from timestamps
        words = [t[0] for t in self.timestamps]
        normalized_words = [normalize(word) for word in words]

        n = len(normalized_words)
        m = len(normalized_search_words)

        # Find the sequence of normalized words in the normalized transcript
        for i in range(n - m + 1):
            if normalized_words[i:i + m] == normalized_search_words:
                start_time = self.timestamps[i][1]  # Start time of the first word
                end_time = self.timestamps[i + m - 1][2]  # End time of the last word
                return start_time, end_time

        return None, None

    # def findStringTimestamps(self, search_string):
    #     words = [t[0] for t in self.timestamps]  # Extract words from tuples
    #     search_words = search_string.split()
    #     n = len(words)
    #     m = len(search_words)

    #     for i in range(n - m + 1):
    #         if words[i:i + m] == search_words:
    #             start_time = self.timestamps[i][1]  # Start time of the first word
    #             end_time = self.timestamps[i + m - 1][2]  # End time of the last word
    #             return start_time, end_time

    #     return None, None

    def cutClip(self, start_time, end_time, output_file):
        runtime = end_time - start_time
        buffer = (45 - runtime) / 2 
        start_time = max(start_time - buffer, 0)
        end_time = end_time + buffer
        subprocess.run([
            "ffmpeg", "-i", self.file, "-ss", str(start_time), "-to", str(end_time), "-c", "copy", output_file
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
