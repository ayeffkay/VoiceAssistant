from googletrans import Translator
import time


def get_translation(text, n_queries=5):
    translator = Translator()
    for _ in range(n_queries):
        try:
            res = translator.translate(text=text, src='ru', dest='en')
            return res.text
        except:
            time.sleep(0.2)
    return 'Not recognized'

