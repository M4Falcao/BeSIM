import json
import os
import pandas as pd
import unicodedata

def load_questions(questions_file="BeSim V2.xlsx") -> dict:
    nome_da_aba = 'perguntas'
    id_column = 'ID'
    id_video = 'video ID'
    question_column = 'pergunta'
    options_columns = ['resposta A', 'resposta B', 'resposta C', 'resposta D']
    correct_answer_column = 'reposta correta'
    questions = {}

    try:
        df = pd.read_excel(questions_file, sheet_name=nome_da_aba)
       
        for indice, linha in df.iterrows():
            video_id = linha[id_video]
            id_pergunta = linha[id_column]
            
            if video_id not in questions:
                questions[video_id] = {}
                
            questions[video_id][id_pergunta] = {
                'question': linha[question_column],
                'options': [linha[col] for col in options_columns],
                'answer': linha[correct_answer_column]
            }
        return questions

    except FileNotFoundError:
        print(f"Erro: O arquivo '{questions_file}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        
def load_video_table(video_file="BeSim V2.xlsx", sheet_name='videos') -> dict:
    """Carrega a tabela de vídeos do arquivo Excel."""
    try:
        df = pd.read_excel(video_file, sheet_name=sheet_name)
        
        video_table = {}
        for index, row in df.iterrows():
            video_table[row['Id']] = {
                'url': row['link'],
                'start': parse_time_to_seconds(row['inicio']),
                'end': parse_time_to_seconds(row['fim']),
                'Obs': row['Obs'] if 'Obs' in row else None
            }
        return video_table
    except FileNotFoundError:
        print(f"Erro: O arquivo '{video_file}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


def createQuestion(question):
    options_index = ["A", "B", "C", "D"]
    question_text = ""
    question_text += (f"Selecione a melhor resposta para a seguinte questão de múltipla escolha com base no vídeo. Sua resposta deve conter apenas um caractere com *somente* com a letra ('A', 'B', 'C' ou 'D') da opção correta.\n")
    question_text += (f"Questão: {question['question']}\n")
    question_text += (f"A melhor resposta é:\n")
    for x in range(len(question['options'])):
        question_text += (f"{options_index[x]} - {question['options'][x]}\n")
    # question_text += (f"Resposta: {question['answer']}\n")
    # question_text += (f"---\n")
    return question_text

def parse_time_to_seconds(time_str: str) -> int:
    """Converte 'HH:MM:SS' para segundos."""
    if(time_str is None or not isinstance(time_str, str)):
        return None
    try:
        parts = list(map(int, time_str.split(':')))
        if len(parts) == 3: return parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2: return parts[0] * 60 + parts[1]
        raise ValueError("Formato de tempo inválido.")
    except (ValueError, IndexError):
        raise ValueError(f"Formato de timestamp inválido: '{time_str}'. Use 'HH:MM:SS'.")

def saveResponses(responses, output_file="responses/responses_model.xlsx"):
    df = pd.DataFrame(responses)

    try:
        # 3. Salvar o DataFrame em um arquivo Excel
        # O argumento `index=False` evita que o pandas salve o índice da linha (0, 1, 2...) como uma coluna no arquivo.
        df.to_excel(output_file, index=False, engine='openpyxl')

        print(f"Dados salvos com sucesso no arquivo '{output_file}'!")

    except Exception as e:
        print(f"Ocorreu um erro ao salvar o arquivo: {e}")
                
                
def loadResponses(output_file="responses/responses.json"):
    # Load existing responses if the file exists
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as file:
            responses = json.load(file)
    else:
        responses = {}
    
    return responses


def addResponses(question_id, response, is_correct, responses):
    if responses is None:
        responses = {
            "question_id": [],
            "response": [],
            "is_correct": [],
        }
    
    responses["question_id"].append(question_id)
    responses["response"].append(response)
    responses["is_correct"].append(is_correct)
    
    return responses

def process_response(string: str) -> str:
    try:
        normalized = unicodedata.normalize('NFD', string)
        
        string_partial = normalized.encode('ascii', 'ignore').decode('utf-8')
        all_letters = [char for char in string_partial if char.isalpha()]
        
        string_only_letters = "".join(all_letters)
        
        string_final = string_only_letters.upper()
        
        if string_final not in ["A", "B", "C", "D"]:
            return string
        
        return string_final
    except Exception as e:
        print(f"Erro ao processar a string: {e}")
        return string


