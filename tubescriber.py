# youtube_transcriber.py

from youtube_transcript_api import YouTubeTranscriptApi

class YouTubeTranscriber:
    def __init__(self):
        pass

    def fetch_youtube_transcript(self, video_id):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return transcript
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def format_transcript(self, transcript):
        formatted_text = ""
        for entry in transcript:
            formatted_text += entry['text'] + " "
        return formatted_text.strip()

    def transcribe(self, video_id):
        transcript = self.fetch_youtube_transcript(video_id)
        if transcript:
            formatted_text = self.format_transcript(transcript)
            return formatted_text
        return None