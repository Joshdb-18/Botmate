import config
import openai

openai.api_key = config.DevelopmentConfig.OPENAI_KEY


def generateChatResponse(prompt):
    messages = []
    messages.append({"role": "system", "content": "Your name is Botmate"
                    "and you are a helpful assistant, you were created by"
                     "Damilola Joshua Oluwafemi a student at alx, he created"
                     "you as a project, and you only answer questions based"
                     "on education."})

    question = {}
    question['role'] = 'user'
    question['content'] = prompt
    messages.append(question)

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                            messages=messages)
    try:
        answer = response['choices'][0]['message']['content']
        answer = answer.replace('\n', '<br>')
    except Exception:
        answer = 'Oops you beat the AI, try a different question,'
        'if the problem persists, come back later.'

    return answer
