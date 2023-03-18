# gpt_srt_translator

Uses chat gpt API to translate a subtitle file (srt) to a different language

Usage:

Generate API key here: https://platform.openai.com/account/api-keys

(It is enough to have a free account for gpt)

install the required packages

```
pip3 install openai beautifulsoup4 tqdm
```

download GptSrtTranslator.py and put it next to your desired python script.

```
from GptSrtTranslator import GptSrtTranslator

GptSrtTranslator.API_KEY = "YOUR_API_KEY"
GptSrtTranslator.MODEL_ENGINE = "gpt-3.5-turbo-0301"

subtitle = GptSrtTranslator(input_file="test.no.srt",
                            output_file="output.srt",
                            input_language="norwegian",
                            output_language="english",
                            # break after 40 characters
                            subtitle_line_max_length=40)

subtitle.translate()
```

Sometimes it merges two subtitles into one causing a shift in the upcoming 1-3 subtitles. Then it sorts itself out and timing is restored.

A little manual compare at the end can easily fix these.
