'''The Main Program for The PhilBott'''

import os
import argparse
import logging
import sys
import yaml

from modules.transcripter import Transcripter
from modules.ragmodelapp import RagModelApp

def setup_logging(level):
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

def load_prompt_file(filename):
    '''Open and read the YAML file'''
    with open(filename, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    return data

def save_transcript_file(filename, script):
    '''Save the Transcript that we've written out'''
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(script)
    print(f"Text saved to {filename}")

# pylint: disable=redefined-outer-name

def generate_transcript(args):
    """Generate transcript from input file."""
    if not args.file:
        logging.error("You must provide an input file using the 'file' command line parameter.")
        sys.exit(0)
    t = Transcripter(os.path.join('', args.file))
    script = t.transcribe()
    return t, script

def get_output_folder(args):
    """Get or create output folder."""
    output_folder = args.outputfolder if args.outputfolder else "outputs"
    if not os.path.exists(output_folder):
        try:
            os.makedirs(output_folder)
        except NotADirectoryError:
            logging.error("Invalid outputfolder parameter ( %s ).", output_folder)
            sys.exit(0)
    return output_folder

def get_config_file(args):
    """Get config file path."""
    return args.config if args.config else "config.yaml"

def prepare_llm(script):
    """Prepare the LLM chain."""
    print("Preparing the LLM...")
    rag = RagModelApp(script)
    rag.prepare_chain()
    return rag



def process_video_clip_quote(quote, index, prompt, t, output_folder):
    """Process a single quote for VideoClipArray."""
    print(f"Index: {index}, Quote: {quote}")
    if not quote:
        return
    q = quote.replace(",","").replace(".","").replace("!","")
    stamp = t.findStringTimestamps(quote)
    print(stamp)
    if stamp[0] is not None and stamp[1] is not None:
        filename = (
            f"{prompt['videoclipnamepattern']}{index}"
            f"{prompt['videoextension']}"
        )
        t.cutClip(stamp[0], stamp[1], os.path.join(output_folder, filename))
    else:
        print(
            "Trying the two halves of the quote because "
            "I can't find the full quote."
        )
        mid = len(q) // 2
        space_index = q.find(' ', mid)
        q1 = q[:space_index]
        print(f"Q1: {q1}")
        q2 = q[space_index:]
        print(f"Q2: {q2}")
        st1 = t.findStringTimestamps(q1)
        st2 = t.findStringTimestamps(q2)
        if st1[0] is not None and st1[1] is not None:
            filename = (
                f"{prompt['videoclipnamepattern']}{index}"
                f"{prompt['videoextension']}"
            )
            t.cutClip(st1[0], st1[1], os.path.join(output_folder, filename))
        elif st2[0] is not None and st2[1] is not None:
            filename = (
                f"{prompt['videoclipnamepattern']}{index}"
                f"{prompt['videoextension']}"
            )
            t.cutClip(st2[0], st2[1], os.path.join(output_folder, filename))
        else:
            print("Couldn't even find half the quote.  Sorry boss.")

def process_video_clip_array(prompt, rag, t, output_folder):
    """Process VideoClipArray type prompts."""
    instructions = (
        prompt['instructions'] +
        " Respond with a pipe-delimited list of the direct transcript quotations ONLY. "
        "Do NOT format or add notes or alter the original text in any way."
    )
    response = rag.invoke(instructions)
    save_transcript_file(
        os.path.join(output_folder, prompt['outputfilename']),
        f"{instructions}:\n\n{response}"
    )

    for index, quote in enumerate(response.split("|")):
        process_video_clip_quote(quote, index, prompt, t, output_folder)

def process_prompts(config, rag, t, output_folder):
    """Process prompts from config."""
    for prompt in config['prompts']:
        match prompt['type']:
            case 'SimpleText':
                save_transcript_file(
                    os.path.join(output_folder, prompt['outputfilename']),
                    f"{prompt['instructions']}:\n\n{rag.invoke(prompt['instructions'])}"
                )
            case 'VideoClipArray':
                process_video_clip_array(prompt, rag, t, output_folder)

def main(args):
    '''Main function to execute the script logic.'''
    setup_logging(logging.ERROR)
    logger = logging.getLogger(__name__)
    logger.info("Starting the script...")

    t, script = generate_transcript(args)
    output_folder = get_output_folder(args)
    config_file = get_config_file(args)
    save_transcript_file(os.path.join(output_folder, "transcript.txt"), script)
    rag = prepare_llm(script)
    config = load_prompt_file(config_file)
    process_prompts(config, rag, t, output_folder)
    logger.info("Script finished successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="The PhilBott!")

    # Add arguments
    parser.add_argument(
        '--file',
        type=str,
        help="Input video file (mp4) if you're using a local file."
    )

    parser.add_argument(
        '--config',
        type=str,
        help="The configuration file of prompts you want to receive."
    )

    parser.add_argument(
        '--outputfolder',
        type=str,
        help="Path / folder name where outputs will be sent. Folder will be created if nonexistent."
    )

    # Parse arguments
    args = parser.parse_args()

    # Execute main function
    main(args)
