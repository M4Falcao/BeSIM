from google import genai
import os
from dotenv import load_dotenv
import json
import utils


# Carrega variáveis do arquivo .env
load_dotenv()
api_key = os.getenv('API_GOOGLE')
client = genai.Client(api_key=api_key)
model = "gemini-2.0-flash"

# Carrega o arquivo JSON de perguntas
json_file_path = "questions/questions.json"
with open(json_file_path, "r", encoding="utf-8") as json_file:
    json_data = json.load(json_file)

responses = utils.loadResponses()
corretas = 0
total = 0
for video in json_data:
    
    print(f"Enviando vídeo: {video}")
    my_file = utils.sendVideo(video, client) # client.files.get(name="files/tepsflgjqdr0")
    print(f"Vídeo enviado: {my_file}")
    
    for question in json_data[video]:
        total += 1
        question_text = utils.createQuestion(question)
        print(f"Enviando pergunta: {question_text}")
        response = utils.callApi(my_file, question_text, client, model)
        
        print()
        print(f"Resposta: {response}")
        print()
        if(response == question["answer"]):
            print("Resposta correta")
            corretas += 1

        # Save the response for the current question
        utils.addResponses(video, question["id"], response, responses)
    
# Save the updated responses back to the file
utils.saveResponses(responses)
print(f"Total de perguntas: {total}")
print(f"Total de respostas corretas: {corretas}")
print(f"Porcentagem de acertos: {corretas/total*100:.2f}%")

# Comparar respostas gravadas com as respostas das questões


