import logging
import math
import re
import time

import openai
from bs4 import BeautifulSoup
from tqdm import tqdm

# Set up logging
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ])

MODEL_ENGINE = "gpt-3.5-turbo-0301"
MAX_TOKENS = 2048

class GptSrtTranslatorIndexed():

    API_KEY = None
    MODEL_ENGINE = None

    skip_square_brackets = True
    # [Cheering]
    skip_all_caps = True
    # LAUGHING

    ignore_asterisks = True
    # * There is a house in New Orleans *
    ignore_note_sings = True
    # ♪ There is a house in New Orleans ♪

    # Break translated lines into two if they are longer than
    subtitle_line_max_length = 50

    # Use the following characters to detect non-english all caps strings
    all_caps_regex = r"^[A-ZÁÉÍÓÖŐÚÜŰ,.!?\- ]{3,}$"

    def __init__(self, **kwargs) -> None:
        openai.api_key = kwargs.get("api_key", self.API_KEY)

        self.srt = {}

        self.slice_length = kwargs.get("slice_length", 10)
        self.relax_time = kwargs.get("relax_time", 0.5)
        self.max_tokens = kwargs.get("max_tokens", MAX_TOKENS)
        self.model_engine = kwargs.get("max_tokens", MODEL_ENGINE)

        self.original_language = kwargs.get("original_language", "english")
        self.target_language = kwargs.get("target_language", "hungarian")

        self.input_file = kwargs.get("input_file", "")
        self.output_file = kwargs.get("output_file", "output.srt")

        logging.info("Starting translation")
        logging.info("Input srt file: %s", self.input_file)
        logging.info("Output srt file: %s", self.output_file)

        if self.input_file:
            self.load_srt()

    def load_srt(self) -> None:
        with open(self.input_file, 'r', encoding="utf8") as f:
            srt_text = f.read()
            # Split the text at every integer which is followed by a timestamp
            parts = re.split(r'(\d+)\n(\d\d:\d\d:\d\d,\d\d\d --> \d\d:\d\d:\d\d,\d\d\d)', srt_text)
            if len(parts) <= 1:
                logging.error("Empty srt file: %s", self.input_file)
                return False

            # Remove any empty parts
            parts = [part for part in parts if part.strip()]

            # Remove BOM
            if parts[0] == '\ufeff':
                del parts[0]

            # Load srt into an object
            self.srt = {}
            index = 0
            for i in range(0,len(parts), 3):
                try:

                    # skip all caps subtitles
                    if self.skip_all_caps:
                        match = re.match(self.all_caps_regex, parts[i+2].strip())
                        if match:
                            logging.debug("Skipping all caps: %s", parts[i+2].strip())
                            continue

                    # skip subtitles in square brackets
                    if self.skip_square_brackets:
                        if parts[i+2].strip().startswith("[") and parts[i+2].strip().endswith("]"):
                            logging.debug("Skipping square brackets: %s", parts[i+2].strip())
                            continue

                    self.srt[index] = {
                        "index": index,
                        "timestamp": parts[i+1].strip(),
                        "original": parts[i+2].strip(),
                        "translated": parts[i+2].strip()
                    }
                except KeyError:
                    print("index error")

                index += 1

    def get_translatable_text(self, start, end) -> str:
        # create a simplified text structure so chatgpt will be able process it
        total = ""
        for i in range(start, end):
            if i >= len(self.srt):
                break

            # Skip musical parts indicated with: *
            if self.ignore_asterisks:
                if self.srt[i]["original"].strip().startswith("*"):
                    continue
            # Skip musical parts indicated with: ♪
            if self.ignore_note_sings:
                if "♪" in self.srt[i]["original"]:
                    continue

            total += str(i) + ": " + self.srt[i]["original"].replace("\n", " ")+"\n"


        # remove all html tags
        soup = BeautifulSoup(total, "html.parser")
        return soup.get_text()

    def break_subtitle_line(self, text):
        """Breaks a subtitle line into two lines if it is longer than the specified maximum length.
        Ignores any HTML tags in the line.
        """
        if len(text) <= self.subtitle_line_max_length:
            return text

        first_line = ''
        second_line = ''

        half_length = math.ceil(len(text) / 2)
        first_half = text[:half_length]
        last_space_index = first_half.rfind(' ')
        first_line_end = half_length if last_space_index == -1 else last_space_index
        first_line = text[:first_line_end].strip()
        second_line = text[first_line_end:].strip()

        # return both lines connected with a line break
        if second_line:
            return f"{first_line}\n{second_line}"

        # second line is empty, return only the first one
        return first_line

    def save_translated_text(self, text):

        # process text received from chatgpt
        for line in text.split('\n'):
            # skip empty lines
            if len(line) == 0:
                continue

            # find index at the beginning of the line
            match = re.match(r'^(\d+): (.*)$', line.strip())

            if match:
                part_index = int(match.group(1))
                text = match.group(2)

                # break dialogs into two lines
                if text.startswith("-"):
                    second_hyphen = text.find("-", text.find("-") + 1)
                    new_text = text[:second_hyphen] + "\n-" + text[second_hyphen+1:]
                    text = new_text
                else:
                    # break long text into two lines
                    text = self.break_subtitle_line(match.group(2))

                self.srt[part_index]["translated"] = text

    def translate(self):
        # translate the subtitle, show a progress bar during translation
        # create title for progress bas, find episode number in string
        match = re.search(r's\d+e\d+', self.input_file, re.IGNORECASE)
        if match:
            title = match.group()
        else:
            title = "video"

        for srt_slice in tqdm(range(0, len(self.srt), self.slice_length), bar_format='{l_bar}{bar:40}{r_bar}', desc=title.ljust(10)):
            logging.info("Slice: %d - %d of %d", srt_slice, srt_slice+self.slice_length-1, len(self.srt))

            text_to_translate = self.get_translatable_text(srt_slice, srt_slice+self.slice_length)

            translated_text = self.chat_gpt_translate(text_to_translate)

            self.save_translated_text(translated_text)

        self.save_srt()

    def save_srt(self):
        srt_content = ""

        for index, subtitle in self.srt.items():
            srt_content += f"{index+1}\n"
            srt_content += f"{subtitle['timestamp']}\n"
            srt_content += f"{subtitle['translated']}\n"
            srt_content += "\n"

        with open(self.output_file, 'w', encoding="utf8") as file:
            file.write(srt_content)

    def chat_gpt_translate(self, text) -> str:
        original_line_count = text.strip().count('\n')+1

        prompt="""Please translate the below """ + self.original_language + """ text,
        make sure you never merge the text from two lines during translation,
        keep the indexes at the beginning of the lines,
        return exactly as many lines as there was in the text to be translated,
        each starting with their original index,
        be concise and translate the lines into """ + f"{self.target_language}:\n{text}"

        logging.debug("Sent %d lines for translation", original_line_count)
        logging.debug("\n%s", prompt)

        # Generate a response
        completion = openai.ChatCompletion.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            # prompt=prompt,
            model=self.model_engine,
            max_tokens=self.max_tokens,
            temperature=0.5,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        response = completion.choices[0]["message"]["content"].strip()
        response_line_count = response.count('\n')+1
        logging.debug("Returned %d lines", response.count('\n')+1)
        if response_line_count != original_line_count:
            logging.warning("Missing %d lines", original_line_count - response_line_count)
            logging.warning("\n\nOriginal:\n%s\nTranslated:\n%s\n\n", text, response)
        else:
            logging.debug("Received %d lines from translation:",response_line_count)
            logging.debug("\n%s", response)

        time.sleep(self.relax_time)
        return response

    def log(self, action, log_text=""):
        log_text = log_text.strip()

        with open('log.txt', 'a', encoding="utf8") as file:
            file.write('------------------\n')
            if len(log_text) > 1:
                file.write(f'Action: {action}\n')
                file.write(f'{log_text}\n')
                line_count = log_text.count('\n')+1
                file.write(f":: {line_count} lines")

