from googletrans import Translator


def get_translation(text):
    translator = Translator()
    try:
        res = translator.translate(text=text, src='ru', dest='en')
        return res.text
    except:
        return 'Not recognized'
