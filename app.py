from flask import Flask, render_template, jsonify, request, Response
import redis
import speech2text
import translate
import pronounce
from collections import OrderedDict


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
db = redis.StrictRedis(host='redis',
                       port=6379, db=0, charset='utf-8', decode_responses=True)
app.config['last_id'] = max(map(int, db.keys())) if len(db.keys()) else 0


@app.route("/")
def index():
    history = OrderedDict(zip(['text', 'translation'], [[], []]))
    for key in sorted(map(int, db.keys())):
        for name, value in db.hgetall(key).items():
            history[name].append(value)
    history = {field: '\n'.join(texts).strip() for field, texts in history.items()}
    return render_template('index.html', data=history)


@app.route("/clear-history")
def clear_history():
    db.flushall()
    return 'nothing'


def add_row(text, translation):
    app.config['last_id'] += 1
    new_id = str(app.config['last_id'])
    text = text.split('\n')[-1]
    translation = translation.split('\n')[-1]
    db.hmset(new_id, {'text': text, 'translation': translation})
    pronounce.text2speech(translation)


@app.route('/translate-text', methods=['POST'])
def translate_text():
    data = request.get_json()
    text = data['text']
    translation = translate.get_translation(text)
    # for simplicity one text row of textarea is considered as one query and the last sentence saved
    add_row(text, translation)

    return jsonify(text=text, translation=translation)


@app.route("/translate-audio", methods=['POST'])
def translate_audio():
    f = request.files['audio_data']
    with open('audio.wav', 'wb') as audio:
        f.save(audio)
    text = speech2text.text_from_audio('audio.wav')
    translation = translate.get_translation(text)
    add_row(text, translation)

    return jsonify(text=text, translation=translation)


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

