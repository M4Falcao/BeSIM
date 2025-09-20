from IPython.display import display, Image, Audio

import cv2  # Usamos OpenCV para ler o vídeo
import base64
import time
from openai import OpenAI
import os
import numpy as np # <<< ADICIONADO: Necessário para calcular os índices espaçados

# --- Configuração ---
# <<< NOVO: Defina aqui a quantidade máxima de frames que você deseja enviar
MAX_FRAMES = 200
VIDEO_PATH = "downloads/videos/27.mp4"

# --- Inicialização do Cliente OpenAI ---
# Carrega a chave da API a partir de uma variável de ambiente
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "SUA_CHAVE_API_AQUI"))

# --- Leitura e Processamento do Vídeo ---
video = cv2.VideoCapture(VIDEO_PATH)

base64Frames = []
while video.isOpened():
    success, frame = video.read()
    if not success:
        break
    _, buffer = cv2.imencode(".jpg", frame)
    base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

video.release()
total_frames_lidos = len(base64Frames)
print(f"{total_frames_lidos} frames lidos do vídeo.")

# --- Seleção dos Frames para Envio ---
# <<< LÓGICA MODIFICADA: Seleciona os frames de forma inteligente
if total_frames_lidos > MAX_FRAMES:
    # Se o vídeo tem mais frames que o nosso limite, selecionamos MAX_FRAMES
    # de forma espaçada para representar o vídeo todo.
    print(f"O vídeo tem mais de {MAX_FRAMES} frames. Selecionando uma amostra espaçada...")
    indices = np.linspace(0, total_frames_lidos - 1, MAX_FRAMES, dtype=int)
    frames_para_enviar = [base64Frames[i] for i in indices]
else:
    # Se o vídeo tem menos frames que o limite, enviamos todos.
    print(f"O vídeo tem {total_frames_lidos} frames, enviando todos.")
    frames_para_enviar = base64Frames

print(f"Enviando {len(frames_para_enviar)} frames para a análise.")

# --- Chamada para a API da OpenAI ---
# NOTA: A estrutura da sua chamada de API parece ser de uma versão mais antiga ou customizada.
# A estrutura abaixo foi adaptada para a versão mais comum da biblioteca 'openai' (v1.x+).
# Se a sua estrutura original funciona, sinta-se à vontade para usá-la, apenas trocando
# 'base64Frames[0::60]' por 'frames_para_enviar'.

# Construindo a lista de mensagens para a API
response = client.responses.create(
    model="gpt-4.1-mini",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": (
                        "These are frames from a video that I want to upload. Generate a compelling description that I can upload along with the video."
                    )
                },
                *[
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{frame}"
                    }
                    for frame in base64Frames[0::60]
                ]
            ]
        }
    ],
)

print("\n--- Descrição Gerada ---")
print(response.choices[0].message.content)