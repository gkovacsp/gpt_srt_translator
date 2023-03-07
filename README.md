# gpt_srt_translator

Usage:

Generate API key here: https://platform.openai.com/account/api-keys

It is enough to have a free account for gpt

create a secret_api.py with your API code or just enter it here directly.

```
import secret_api

from GptSrtTranslator import GptSrtTranslator

GptSrtTranslator.API_KEY = secret_api.openai_api_key
GptSrtTranslator.MODEL_ENGINE = "gpt-3.5-turbo-0301"

subtitle = GptSrtTranslator(input_file="test.no.srt",
                            original_language="norwegian",
                            target_language="english",
                            output_file="output.srt")

subtitle.translate()
```
