import logging

from GptSrtTranslator import GptSrtTranslator

import secret_api

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Generate API key here: https://platform.openai.com/account/api-keys
# It is enough to have a free account for gpt

GptSrtTranslator.API_KEY = secret_api.openai_api_key
GptSrtTranslator.MODEL_ENGINE = "gpt-3.5-turbo-0301"

subtitle = GptSrtTranslator(input_file="input.en.srt",
                            output_file="output.hu.srt",
                            input_language="English",
                            output_language="Hungarian",
                            # break after 40 characters
                            subtitle_line_max_length=40)

subtitle.slice_length = 25
subtitle.translate()
