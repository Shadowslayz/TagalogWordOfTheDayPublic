# Install
pip install TTS

# Basic usage
from TTS.api import TTS
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
tts.tts_to_file(text="Hello, world!", file_path="output.wav")