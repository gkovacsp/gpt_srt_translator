import argparse

from GptSrtTranslator import GptSrtTranslator

parser = argparse.ArgumentParser(description='Translate SRT subtitle using OpenAI GPT API.')

parser.add_argument('--openai_api_key', '-a', type=str, required=True, help='API key for OpenAI')
parser.add_argument('--input_file', '-f', type=str, required=True, help='Input SRT file path')
parser.add_argument('--input_language','-i',  type=str, required=True, help='Language of input SRT file')

parser.add_argument('--output_file', '-s', type=str, default="output.srt", help='Output SRT file path, default: output.srt')
parser.add_argument('--output_language', '-o', type=str, default="English", help='Language to translate to, default: English')
parser.add_argument('--break_long_lines_at', '-b', type=int, default=40, help='Maximum length of output lines, default: 40')
parser.add_argument('--slice_length', '-l', type=int, default=15, help='Number of subtitles to send together, default: 15')

args = parser.parse_args()

# Print out the parsed arguments
print("-------------------------------------------")
print("         OpenAI API key: ", args.openai_api_key)
print("             Input file: ", args.input_file)
print("         Input language: ", args.input_language)
print("-------------------------------------------")
print("            Output file: ", args.output_file)
print("        Output language: ", args.output_language)
print("Break lines longer than: ", args.break_long_lines_at)
print("           Slice length: ", args.slice_length)
print("-------------------------------------------")

GptSrtTranslator.API_KEY = args.openai_api_key
GptSrtTranslator.MODEL_ENGINE = "gpt-3.5-turbo-0301"

subtitle = GptSrtTranslator(input_file=args.input_file,
                            output_file=args.output_file,
                            input_language=args.input_language,
                            output_language=args.output_language,
                            subtitle_line_max_length=args.break_long_lines_at)

subtitle.slice_length = 25
subtitle.translate()
