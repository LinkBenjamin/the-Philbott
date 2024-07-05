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
    # Open and read the YAML file
    with open(filename, 'r') as file:
        data = yaml.safe_load(file)
    return data

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
    
    if args.file:
        t = Transcripter(args.file)
        script = t.transcribe()
    else:
        logger.error("You must provide an input file using the 'file' command line parameter.")
        sys.exit(0)
    
    if args.outputfolder:
        output_folder = args.outputfolder
    else:
        output_folder = "outputs"

    if args.config:
        config_file = args.config
    else:
        config_file = "config.yaml"

    if not os.path.exists(output_folder):
        try:
            os.makedirs(output_folder)
        except NotADirectoryError:
            logger.error(f"The content of the outputfolder parameter ( {output_folder} ) was not valid.  A directory cannot be constructed there.")
            sys.exit(0)

    saveTranscriptFile(os.path.join(output_folder,"transcript.txt"), script)

    print("Preparing the LLM...")
    rag = RagModelApp(script)
    rag.prepare_chain()

    config = load_prompt_file(config_file)
    
    for prompt in config['prompts']:
        if prompt['type'] == 'SimpleText':
            saveTranscriptFile(os.path.join(output_folder,prompt['outputfilename']), f"{prompt['instructions']}:\n\n{rag.invoke(prompt['instructions'])}")

        if prompt['type'] == 'VideoClipArray':
            instructions = prompt['instructions'] + " Respond with a pipe-delimited list of the direct transcript quotations ONLY.  Do NOT format or add notes or alter the original text in any way."
            response = rag.invoke(instructions)
            saveTranscriptFile(os.path.join(output_folder,prompt['outputfilename']), f"{instructions}:\n\n{response}")
            
            y = response.split("|")
            for index, quote in enumerate(y):
                print(f"Index: {index}, Quote: {quote}")
                if quote:
                    q = quote.replace(",","").replace(".","").replace("!","")
                    stamp = t.findStringTimestamps(quote)
                    print(stamp)
                    if stamp[0] is not None and stamp[1] is not None:
                        filename = f"{prompt['videoclipnamepattern']}{index}{prompt['videoextension']}"
                        t.cutClip(stamp[0], stamp[1], os.path.join(output_folder, filename))
                    else:
                        print("Skipping because None is one of the stamps.")

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
        help="Path and folder name where the outputs will be sent.  The folder will be created if it doesn't exist."
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute main function
    main(args)