import json
import os


def createQuestion(question):
    options_index = ["A", "B", "C", "D"]
    question_text = ""
    question_text += (f"Selecione a melhor resposta para a seguinte questão de múltipla escolha com base no vídeo. Responda apenas com a letra (A, B, C ou D) da opção correta.\n")
    question_text += (f"Questão: {question['question']}\n")
    question_text += (f"A melhor resposta é:\n")
    for x in range(len(question['options'])):
        question_text += (f"{options_index[x]} - {question['options'][x]}\n")
    # question_text += (f"Resposta: {question['answer']}\n")
    # question_text += (f"---\n")
    return question_text

def callApi(myfile, question, client, model):
    
    response = client.models.generate_content(
        model= model, contents=[myfile, question]
    )

    return (response.text)


def sendVideo(video_name, client):
    my_file = client.files.upload(file=f"videos/{video_name}.mp4")
    while(True):
        my_file = client.files.get(name=my_file.name)
        if my_file.status == "ACTIVE":
            return my_file


def saveResponses(responses, output_file="responses.json"):
            # Save the updated responses back to the file
            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(responses, file, ensure_ascii=False, indent=4)
                
                
def loadResponses(output_file="responses.json"):
    # Load existing responses if the file exists
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as file:
            responses = json.load(file)
    else:
        responses = {}
    
    return responses


def addResponses(video_name, question_id, response, responses):
    # Load existing responses if the file exists

    # Add the response to the corresponding video and question
    if video_name not in responses:
        responses[video_name] = []
    
    responses[video_name].append({
        "question": question_id,
        "response": response
    })
    
    return responses

    