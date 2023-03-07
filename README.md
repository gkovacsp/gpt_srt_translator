# gpt_srt_translator

Uses chat gpt API to translate a subtitle file (srt) to a different language

Usage:

Generate API key here: https://platform.openai.com/account/api-keys

It is enough to have a free account for gpt

```
from GptSrtTranslator import GptSrtTranslator

GptSrtTranslator.API_KEY = "YOUR_API_KEY"
GptSrtTranslator.MODEL_ENGINE = "gpt-3.5-turbo-0301"

subtitle = GptSrtTranslator(input_file="test.no.srt",
                            original_language="norwegian",
                            target_language="english",
                            output_file="nor-to-eng.srt")

subtitle.translate()
```
