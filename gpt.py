# video_analyzer_gpt.py
# Um script simples para analisar um vídeo local usando o modelo GPT-4o da OpenAI.

import cv2
import base64
import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# --- CONFIGURAÇÃO ---

# Carrega as variáveis de ambiente (onde sua chave da API está)
load_dotenv()

# Intervalo entre os frames a serem capturados (em milissegundos).
# 1000ms = 1 frame por segundo. Aumente para vídeos longos para economizar custos.
FRAME_INTERVAL_MS = 1000

# --- FUNÇÕES ---

def extract_frames_from_video(video_path: str) -> list[str]:
    """
    Extrai frames de um vídeo em intervalos regulares e os codifica em base64.
    
    Args:
        video_path: O caminho para o arquivo de vídeo local.

    Returns:
        Uma lista de strings, onde cada string é um frame codificado em base64.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Vídeo não encontrado no caminho: {video_path}")

    logging.info(f"Iniciando extração de frames do vídeo: {video_path}")
    
    video_capture = cv2.VideoCapture(video_path)
    base64_frames = []
    last_captured_time = 0

    while video_capture.isOpened():
        success, frame = video_capture.read()
        if not success:
            break

        current_time_ms = video_capture.get(cv2.CAP_PROP_POS_MSEC)
        
        if current_time_ms - last_captured_time >= FRAME_INTERVAL_MS:
            last_captured_time = current_time_ms
            
            # Codifica o frame para JPEG em memória
            _, buffer = cv2.imencode(".jpg", frame)
            
            # Converte para base64
            base64_frame = base64.b64encode(buffer).decode("utf-8")
            base64_frames.append(base64_frame)
            
    video_capture.release()
    logging.info(f"Extração concluída. {len(base64_frames)} frames capturados.")
    return base64_frames


def analyze_video_with_gpt4o(base64_frames: list[str], prompt_text: str) -> str:
    """
    Envia os frames de um vídeo e uma pergunta para o modelo GPT-4o.
    
    Args:
        base64_frames: Uma lista de frames codificados em base64.
        prompt_text: A pergunta ou comando para a análise.
        
    Returns:
        A resposta em texto gerada pelo modelo.
    """
    try:
        client = OpenAI() # O cliente usa a chave do .env automaticamente

        # Monta a requisição para a API
        # O primeiro item da lista de conteúdo é o texto, seguido pelas imagens
        prompt_messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    *map(lambda frame: {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame}", "detail": "low"}}, base64_frames),
                ],
            },
        ]

        logging.info("Enviando requisição para a API do GPT-4o...")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini", # O modelo multimodal mais recente
            messages=prompt_messages,
        )
        
        return response.choices[0].message.content

    except Exception as e:
        logging.error(f"Ocorreu um erro ao chamar a API da OpenAI: {e}")
        return "Erro ao processar a análise do vídeo."


# --- EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s', filename='gpt.log')

    # --- EDITE ESTAS VARIÁVEIS ---
    VIDEO_PATH = "downloads/videos/3.mp4"  # Coloque o nome do seu arquivo de vídeo aqui
    USER_PROMPT = "O que fez com que uma musica fosse cantada ao final da interação?"
    # -----------------------------

    # Passo 1: Extrair os frames do vídeo
    try:
        frames = extract_frames_from_video(VIDEO_PATH)

        if not frames:
            logging.warning("Nenhum frame foi extraído. Verifique o arquivo de vídeo e o intervalo.")
        else:
            # Passo 2: Enviar os frames para análise
            analysis_result = analyze_video_with_gpt4o(frames, USER_PROMPT)
            
            # Passo 3: Imprimir o resultado
            print("\n" + "="*20 + " ANÁLISE DO VÍDEO " + "="*20)
            print(analysis_result)
            print("="*62)

    except FileNotFoundError as e:
        logging.error(e)
    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado no processo: {e}")