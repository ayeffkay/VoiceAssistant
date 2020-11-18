from google.cloud import speech_v1 as speech
import os
import io

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'key.json'
config = dict(
    audio_channel_count=1,
    language_code="ru-RU",
    enable_automatic_punctuation=True,
    enable_word_time_offsets=True,
)


def speech2text(audio):
    client = speech.SpeechClient()
    try:
        response = client.recognize(config=config, audio=audio)
        sents = get_sentences(response)
        return sents
    except:
        return 'Not recognized'


def get_sentences(response):
    sents = ' '.join(result.alternatives[0].transcript for result in response.results)
    return sents


def text_from_audio(wav_fname):
    with io.open(wav_fname, "rb") as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)
    return speech2text(audio)
