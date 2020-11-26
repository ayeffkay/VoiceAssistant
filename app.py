from flask import Flask, render_template, jsonify, request, Response
import redis
import speech2text
import translate
import pronounce


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
db = redis.StrictRedis(host='redis',
                       port=6379, db=0, charset='utf-8', decode_responses=True)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/clear-history")
def clear_history():
    db.flushall()
    return 'nothing'


def add_row(text, translation):
    text = text.split('\n')[-1]
    translation = translation.split('\n')[-1]
    db.mset({text: translation})
    pronounce.text2speech(translation)


def make_translation(text):
    loaded_from_cache = False
    last = text.split('\n')[-1]
    if db.exists(last):
        translation = db.get(last)
        loaded_from_cache = True
    else:
        translation = translate.get_translation(text)
        if translation != 'Not recognized':
            # for simplicity one text row of textarea is considered as one query and the last sentence saved
            add_row(text, translation)
    return translation, loaded_from_cache


@app.route('/translate-text', methods=['POST'])
def translate_text():
    data = request.get_json()
    text = data['text']
    translation, cache_flag = make_translation(text)

    return jsonify(text=text, translation=translation, cache_flag=cache_flag)


@app.route("/translate-audio", methods=['POST'])
def translate_audio():
    f = request.files['audio_data']
    with open('audio.wav', 'wb') as audio:
        f.save(audio)
    text = speech2text.text_from_audio('audio.wav')
    translation, cache_flag = make_translation(text)

    return jsonify(text=text, translation=translation, cache_flag=cache_flag)


@app.route('/play-audio')
def play_audio():
    def generate():
        with open('output.wav', 'rb') as audio:
            chunk = audio.read(1024)
            while chunk:
                yield chunk
                chunk = audio.read(1024)

    return Response(generate(), mimetype='audio/x-wav')


"""
@app.route('/play-audio')
def play_audio():
    if os.path.exists('output.wav'):
        with open('output.wav', 'rb') as audio:
            data = base64.b64encode(audio.read()).decode('UTF-8')

            res = app.response_class(response=json.dumps(data),
                                     status=200,
                                     mimetype='application/json')
        return res
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", threaded=True, debug=True)

