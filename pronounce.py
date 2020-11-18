from gtts import gTTS


def text2speech(text):
    language = 'en'
    output_filename = 'output.wav'
    speech = gTTS(text=text, lang=language, slow=False)
    speech.save(output_filename)
    return output_filename
