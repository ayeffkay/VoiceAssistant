from flask import Flask, render_template, jsonify, request, Response
import redis
import speech2text
import translate
import pronounce

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
db = redis.StrictRedis(host='redis',
                       port=6379, db=0, charset='utf-8', decode_responses=True)
app.config['last_id'] = max(map(int, db.keys())) if len(db.keys()) else 0


@app.route("/")
def index():
    history = dict(zip(['text', 'translation'], [[], []]))
    for key in sorted(map(int, db.keys())):
        for name, value in db.hgetall(key).items():
            history[name].append(value)
    history = {name: '\n'.join(history[name]).strip() for name in history}
    return render_template('index.html', data=history)


@app.route("/clear-history")
def clear_history():
    db.flushall()
    return 'nothing'


def add_row(text):
    app.config['last_id'] += 1
    last_translation = translate.get_translation(text)
    new_id = str(app.config['last_id'])
    db.hmset(new_id, {'text': text, 'translation': last_translation})
    output_filename = pronounce.text2speech(last_translation)
    return output_filename


@app.route('/translate-text', methods=['POST'])
def translate_text():
    data = request.get_json()
    text = data['text']
    translation = translate.get_translation(text)

    # for simplicity one text row of textarea is considered as one query and the last sentence saved
    add_row(text.split('\n')[-1])
    return jsonify(text=text, translation=translation)


@app.route("/translate-audio", methods=['POST'])
def translate_audio():
    f = request.files['audio_data']
    with open('audio.wav', 'wb') as audio:
        f.save(audio)
    text = speech2text.text_from_audio('audio.wav')
    translation = translate.get_translation(text)
    add_row(text)

    return jsonify(text=text, translation=translation)


@app.route('/play_audio')
def play_audio():
    def generate():
        with open('output.wav', 'rb') as audio:
            data = audio.read(1024)
            while data:
                yield data
                data = audio.read(1024)

    return Response(generate(), mimetype='audio/wav')


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

