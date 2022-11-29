import whisper
import pydub
import os

whisper_model = "medium"


def load_model():
    print("Loading audio model...")
    return whisper.load_model(whisper_model)


def audio_to_text(model, audio_file):
    audio = pydub.AudioSegment.from_file(audio_file)
    # Export for loading later
    audio.export("audio_tmp")
    try:
        audio = whisper.load_audio("audio_tmp")
        result = whisper.transcribe(model=model, audio=audio, verbose=True)
    finally:
        os.remove("audio_tmp")
    return result["text"]
