import argparse
import logging
import sys
import json

from transcripter import Transcripter
from tubescriber import YouTubeTranscriber
from ragmodelapp import RagModelApp

def setup_logging(level=logging.ERROR):
    """
    Set up the logging configuration.
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def saveTranscriptFile(filename, script):
    with open(filename, 'w') as file:
        file.write(script)
    print(f"Text saved to {filename}")

def main(args):
    """
    Main function to execute the script logic.
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting the script...")
    
    # Example functionality
    if args.file:
        t = Transcripter(args.file)
        script = t.transcribe()

    if args.youtubeid:
        t = YouTubeTranscriber()
        script = t.transcribe(args.youtubeid)
    else:
        logger.info("In order to use this application, you must call it with the 'file' or the 'youtubeid' parameter.\n\nEx: python main.py --file='sample.mp4'\nEx 2: python main.py --youtubeid=ADSFJNKKLASDG")
    
    saveTranscriptFile("transcript.txt", script)

    print("Preparing the LLM...")
    rag = RagModelApp(script)
    rag.prepare_chain()
    
    prompt1 = "Summarize this content in 4-5 sentences.  What are the main themes?"
    saveTranscriptFile("Summary.txt", f"{prompt1}:\n\n{rag.invoke(prompt1)}")

    prompt2 = "Create a clickbait-style title for this content based on its main themes."
    saveTranscriptFile("Title.txt", f"{prompt2}:\n\n{rag.invoke(prompt2)}")
    
    prompt3 = "Select 3 potential quotable moments that would make great short-form social media content.  Respond with a pipe-delimited list of the direct transcript quotations ONLY.  Do NOT format or add notes or alter the original text in any way."
    x = rag.invoke("Select 3 potential quotable moments that would make great short-form social media content.  Respond with a pipe-delimited list of the direct transcript quotations ONLY.  Do NOT format or add notes or alter the original text in any way.")
    saveTranscriptFile("Quotables.txt", f"{prompt3}:\n\n{rag.invoke(prompt3)}")

    y = x.split("|")
    for index, quote in enumerate(y):
        print(f"Index: {index}, Quote: {quote}")
        if quote:
            q = quote.replace(",","").replace(".","").replace("!","")
            stamp = t.findStringTimestamps(quote)
            print(stamp)
            if stamp[0] is not None and stamp[1] is not None:
                filename = f"q{index}.mp4"
                t.cutClip(stamp[0], stamp[1], filename)
            else:
                print("Skipping because None is one of the stamps.")

    logger.info("Script finished successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="The PhilBott!")
    
    # Add arguments
    parser.add_argument(
        '--file',
        type=str,
        help="Input video file (mp4) if you're using a local file"
    )

    parser.add_argument(
        '--youtubeid',
        type=str,
        help="Youtube video id if you're using a youtube video as input"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute main function
    main(args)