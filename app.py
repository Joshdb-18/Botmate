from flask import Flask, render_template, jsonify, request
import config
import openai
import aiapi

openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who won the world series in 2020?"},
        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
        {"role": "user", "content": "Where was it played?"}
    ]
)

def page_not_found(e):
  return render_template('404.html'), 404


app = Flask(__name__)
app.config.from_object(config.config['development'])

app.register_error_handler(404, page_not_found)


@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
        prompt = request.form['prompt']
        res = {}
        res['answer'] = generateChatResponse(prompt)
        return jsonify(res), 200

    return render_template('index.html', **locals())

def generateChatResponse(prompt):
    messages = []
    messages.append({"role": "system", "content": "Your name is Karabo. You are a helpful assistant."})

    question = {}
    question['role'] = 'user'
    question['content'] = prompt
    messages.append(question)

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=messages)

    try:
        answer = response['choices'][0]['message']['content'].replace('\n', '<br>')
    except:
        answer = 'Oops you beat the AI, try a different question, if the problem persists, come bacl later.'

    return answer

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8888', debug=True)
