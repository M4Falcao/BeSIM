import sys
import time
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
import json
import utils
import logging

ID_STORAGE_FILE = "uploaded_video_ids.txt"

# --- Funções de Gerenciamento da API ---

def upload_video(file_path: str, client) -> str | None:
    """
    Faz o upload de um arquivo de vídeo para o serviço de arquivos do Gemini,
    aguarda o processamento e retorna o ID único do arquivo.
    """
    logging.info(f"Iniciando o upload do arquivo: {file_path}")
    if not os.path.exists(file_path):
        logging.error(f"Arquivo não encontrado: {file_path}")
        return None

    video_file = None
    try:
        video_file = client.files.upload(file=file_path)
        logging.info(
            f"Arquivo enviado. Aguardando processamento... (ID temporário: {video_file.name})"
        )

        while video_file.state.name == "PROCESSING":
            time.sleep(5)
            video_file = client.files.get(name=video_file.name)

        if video_file.state.name == "FAILED":
            logging.error(f"O processamento do arquivo '{file_path}' na API falhou.")
            return None

        logging.info(f"✅ Arquivo processado com sucesso! ID Final: {video_file.name}")
        save_video_id(video_file.name)

        return video_file

    except Exception as e:
        logging.error(f"Ocorreu um erro durante o upload: {e}")
        if video_file:
            client.files.delete(name=video_file.name)
            logging.warning(
                f"Tentativa de limpeza do arquivo com falha '{video_file.name}' na API."
            )
        return None


def save_video_id(file_id: str):
    """
    Salva (anexa) um ID de arquivo em um arquivo de texto local.
    """
    if not file_id:
        logging.warning("ID do arquivo está vazio. Nada para salvar.")
        return

    try:
        with open(ID_STORAGE_FILE, "a") as f:
            f.write(f"{file_id}\n")
        logging.info(f"ID '{file_id}' salvo com sucesso em '{ID_STORAGE_FILE}'.")
    except IOError as e:
        logging.error(f"Não foi possível escrever no arquivo de log de IDs: {e}")


def get_video_by_id(file_id: str, client):
    """Busca e exibe os metadados de um arquivo específico na API pelo seu ID."""
    logging.info(f"Buscando metadados para o arquivo ID: {file_id}...")
    try:
        file = client.files.get(name=file_id)
        return file
    except Exception as e:
        logging.error(f"Ocorreu um erro ao buscar o arquivo: {e}")


def list_all_videos(client) -> list[types.File] | None:
    """Lista todos os arquivos de vídeo atualmente no serviço de arquivos do Gemini."""
    logging.info("Listando todos os arquivos na API do Gemini...")
    try:
        files = list(client.files.list())
        if not files:
            logging.info(
                "Nenhum arquivo encontrado na sua conta do Gemini File Service."
            )
            return

        print("-" * 50)
        print(f"Encontrados {len(files)} arquivos:")
        for file in files:
            print(
                f"  - ID: {file.name}, Nome: {file.display_name}, Estado: {file.state.name} , Created: {file.uri}"
            )
        print("-" * 50)
        return files
    except Exception as e:
        logging.error(f"Ocorreu um erro ao listar os arquivos: {e}")


def delete_video_by_id(file_id: str, client):
    """Deleta um arquivo específico da API do Gemini pelo seu ID."""
    logging.info(f"Tentando deletar o arquivo ID: {file_id}...")
    try:
        client.files.delete(name=file_id)
        logging.info(f"✅ Arquivo '{file_id}' deletado com sucesso da API.")
    except Exception as e:
        logging.error(f"Ocorreu um erro ao deletar o arquivo: {e}")


def callApi(file, question_text, model, client):
    """Chama a API do Gemini para responder a uma pergunta baseada em um vídeo."""
    while True:
        try:
            response = client.models.generate_content(
                model=model, contents=[file, question_text]
            )
            break
        except Exception as e:
            print(f"Erro: {e}")
            print("Tentando novamente...")
            time.sleep(5)
            continue

    return response.text

def loadUploadedVideoIds(file_path) -> dict:
    """Carrega os IDs de vídeos já enviados para a API do Gemini."""
    
    print(f"Carregando IDs de vídeos do arquivo: {file_path}")
    if not os.path.exists(file_path):
        return {}

    with open(file_path, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            print(f"Erro ao decodificar o arquivo JSON: {file_path}. Retornando dicionário vazio.")
            return {}
        
def saveUploadedVideoIds(ids: dict, file_path):
    """Salva os IDs de vídeos enviados para a API do Gemini em um arquivo JSON."""
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(ids, file, ensure_ascii=False, indent=4)
    print(f"IDs de vídeos salvos com sucesso em '{file_path}'.")

def main():
    # Carrega variáveis do arquivo .env
    load_dotenv()
    api_key = os.getenv("API_GOOGLE")
    client = genai.Client(api_key=api_key)
    model = "gemini-1.5-pro"
    
    TABLE = "BeSimV5.xlsx"
    ID_STORAGE_FILE = "log/uploaded_video_ids_gemini.json"

    # Carrega o arquivo JSON de perguntas
    questions = utils.load_questions(TABLE)
    videos = utils.load_video_table(TABLE)
    ids_gemini = loadUploadedVideoIds(ID_STORAGE_FILE)

    responses = None
    corretas = 0
    total = 0
    for video_id in videos:
        external_name =  ids_gemini[str(video_id)] if str(video_id) in ids_gemini else None
        print(f"Processando vídeo: {video_id}")

        media = get_video_by_id(external_name, client) if external_name is not None else None

        if not media:
            path = f"downloads/videos/{str(int(video_id))}.mp4"
            if not os.path.exists(path):
                print(f"Arquivo de vídeo não encontrado: {path}. Pulando...")
                continue

            print(f"Enviando vídeo: {video_id}")
            media = upload_video(path, client)
            print(f"Vídeo enviado: {media.name}")
            ids_gemini[video_id] = media.name
            
        else:
            print(f"Vídeo encontrado: {media.name}")
            

        for question_id in questions[video_id]:
            question = questions[video_id][question_id]
            correct = False
            total += 1
            question_text = utils.createQuestion(question)
            print(f"Enviando pergunta: \n{question_text}")
            response = callApi(media, question_text, model, client)
            response = utils.process_response(response)
            print()
            print(f"Resposta: {response}")
            print()
            if response == question["answer"]:
                correct = True
                print("Resposta correta")
                corretas += 1

            # Save the response for the current question
            responses = utils.addResponses(question_id, response, correct, responses)

    # Save the updated responses back to the file
    utils.saveResponses(responses, f"responses/responses_{model}.xlsx")
    saveUploadedVideoIds(ids_gemini, ID_STORAGE_FILE)
    print(f"Total de perguntas: {total}")
    print(f"Total de respostas corretas: {corretas}")
    print(f"Porcentagem de acertos: {corretas/total*100:.2f}%")
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", filename="log/gemini.log", filemode="w")
    try:
        main()
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado: {e}")
        sys.exit(1)