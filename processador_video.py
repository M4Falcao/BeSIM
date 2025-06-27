# -*- coding: utf-8 -*-

"""
Processador de Vídeo Automatizado
=================================

Este script de linha de comando extrai frames, transcreve áudio usando a API Gemini
e cria uma "tirinha" de imagens a partir de um arquivo de vídeo.

Uso:
    python processador_video.py /caminho/para/seu/video.mp4

Pré-requisitos:
    - Python 3.8+
    - Bibliotecas: pip install opencv-python-headless moviepy Pillow google-generativeai
    - Chave de API do Gemini configurada na variável de ambiente GOOGLE_API_KEY.
"""

import os
import sys
import argparse
import cv2
import time
from moviepy import VideoFileClip
from PIL import Image
import google.generativeai as genai

# --- Configurações ---
# Use um valor inteiro (ex: 2 para 2 frames/seg) ou fracionário
# (ex: 0.5 para 1 frame a cada 2 segundos).
FRAMES_POR_SEGUNDO = 1

# --- Funções Modulares ---

def extrair_frames(caminho_video: str, pasta_saida: str, fps_extracao: float) -> int:
    """
    Extrai frames de um vídeo a uma taxa especificada e os salva como imagens.

    Args:
        caminho_video (str): O caminho para o arquivo de vídeo.
        pasta_saida (str): O diretório onde os frames serão salvos.
        fps_extracao (float): A quantidade de frames a serem extraídos por segundo.

    Returns:
        int: O número de frames extraídos com sucesso.
    """
    print(f"INFO: Iniciando extração de frames a {fps_extracao} FPS...")

    if not os.path.exists(caminho_video):
        print(f"ERRO: Arquivo de vídeo não encontrado em '{caminho_video}'")
        raise FileNotFoundError(f"Arquivo de vídeo não encontrado: {caminho_video}")

    video = cv2.VideoCapture(caminho_video)
    if not video.isOpened():
        print("ERRO: Não foi possível abrir o arquivo de vídeo.")
        return 0

    fps_video_original = video.get(cv2.CAP_PROP_FPS)
    if fps_video_original == 0:
        print("ERRO: Não foi possível ler o FPS do vídeo. Usando valor padrão de 30.")
        fps_video_original = 30 # Valor de fallback

    # Calcula o intervalo entre os frames a serem salvos
    intervalo_frames = int(fps_video_original / fps_extracao)
    if intervalo_frames < 1:
        intervalo_frames = 1

    contador_frames_total = 0
    contador_frames_salvos = 0

    while True:
        sucesso, frame = video.read()
        if not sucesso:
            break  # Fim do vídeo

        if contador_frames_total % intervalo_frames == 0:
            nome_arquivo_frame = os.path.join(pasta_saida, f"frame_{contador_frames_salvos:04d}.jpg")
            cv2.imwrite(nome_arquivo_frame, frame)
            contador_frames_salvos += 1

        contador_frames_total += 1

    video.release()
    print(f"INFO: Extração de frames concluída. {contador_frames_salvos} frames salvos.")
    return contador_frames_salvos

def transcrever_audio(caminho_video: str, pasta_saida: str):
    """
    Extrai o áudio, envia para a API Gemini para transcrição e salva como SRT.

    Esta função implementa um mecanismo robusto que aguarda o processamento do
    arquivo pela API antes de solicitar a transcrição.

    Args:
        caminho_video (str): O caminho para o arquivo de vídeo.
        pasta_saida (str): O diretório onde o arquivo de legenda .srt será salvo.
    """
    print("INFO: Iniciando extração e transcrição de áudio...")
    caminho_audio_temp = os.path.join(pasta_saida, "audio_temp.mp3")
    caminho_srt = os.path.join(pasta_saida, "legendas.srt")

    try:
        # 1. Extração de áudio com MoviePy
        with VideoFileClip(caminho_video) as video:
            if video.audio is None:
                print("AVISO: O vídeo não possui uma faixa de áudio. Pulando a transcrição.")
                return

            print("INFO: Extraindo faixa de áudio...")
            video.audio.write_audiofile(caminho_audio_temp, logger=None)

        # 2. Configuração e chamada da API Gemini
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("ERRO: A variável de ambiente GOOGLE_API_KEY não está definida.")
            return

        genai.configure(api_key=api_key)

        print("INFO: Fazendo upload do arquivo de áudio para a API Gemini...")
        audio_file = genai.upload_file(path=caminho_audio_temp)

        # 3. Espera ativa pelo processamento do arquivo
        print(f"INFO: Arquivo '{audio_file.name}' em processamento. Aguardando ficar ativo...")
        timeout_segundos = 300  # 5 minutos de timeout
        inicio_espera = time.time()

        while audio_file.state.name == "PROCESSING":
            if time.time() - inicio_espera > timeout_segundos:
                print(f"ERRO: Timeout de {timeout_segundos}s atingido. O processamento do arquivo falhou.")
                return

            time.sleep(5)  # Aguarda 5 segundos antes de verificar novamente
            audio_file = genai.get_file(name=audio_file.name)

        if audio_file.state.name == "FAILED":
            print("ERRO: A API falhou ao processar o arquivo de áudio.")
            return

        print(f"INFO: Arquivo pronto para transcrição (Estado: {audio_file.state.name}).")

        # 4. Geração do conteúdo (transcrição)
        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
        prompt = (
            "Transcreva o áudio a seguir na íntegra. "
            "A saída deve ser estritamente no formato de legendas SubRip (.srt). "
            "Use timestamps precisos com milissegundos. Não adicione comentários ou texto extra.\n"
            "Exemplo do formato esperado:\n"
            "1\n"
            "00:00:01,234 --> 00:00:04,567\n"
            "Este é o primeiro segmento da legenda.\n\n"
            "2\n"
            "00:00:05,111 --> 00:00:08,999\n"
            "E aqui continua o segundo segmento.\n"
        )

        print("INFO: Enviando prompt para o modelo Gemini...")
        response = model.generate_content([prompt, audio_file])

        # 5. Salvando a transcrição no arquivo SRT
        with open(caminho_srt, "w", encoding="utf-8") as f:
            f.write(response.text)

        print(f"INFO: Transcrição salva com sucesso em '{caminho_srt}'.")

    except FileNotFoundError:
        # Esse erro já é tratado em extrair_frames, mas é bom ter aqui por segurança.
        print(f"ERRO: Arquivo de vídeo não encontrado em '{caminho_video}'")
    except Exception as e:
        # Captura outras exceções (API, MoviePy, etc.)
        print(f"ERRO: Ocorreu uma falha inesperada durante a transcrição: {e}")
        # Tenta remover o arquivo de legenda incompleto, se existir
        if os.path.exists(caminho_srt):
            os.remove(caminho_srt)
    finally:
        # 6. Limpeza do arquivo de áudio temporário
        if os.path.exists(caminho_audio_temp):
            os.remove(caminho_audio_temp)
            print("INFO: Arquivo de áudio temporário removido.")


def criar_tirinha(pasta_frames: str, pasta_saida: str):
    """
    Combina todos os frames de uma pasta em uma única imagem horizontal.

    Args:
        pasta_frames (str): O diretório contendo os frames extraídos.
        pasta_saida (str): O diretório onde a imagem final será salva.
    """
    print("INFO: Iniciando criação da tirinha de imagens...")
    caminho_tirinha = os.path.join(pasta_saida, "tirinha_completa.png")

    try:
        # Lista e ordena os arquivos de frame para garantir a sequência correta
        arquivos_frame = sorted(
            [f for f in os.listdir(pasta_frames) if f.startswith("frame_") and f.endswith(".jpg")]
        )

        if not arquivos_frame:
            print("AVISO: Nenhum frame encontrado para criar a tirinha. Pulando esta etapa.")
            return

        # Abre as imagens e as armazena em uma lista
        imagens = [Image.open(os.path.join(pasta_frames, f)) for f in arquivos_frame]

        # Calcula as dimensões da imagem final
        largura_total = sum(img.width for img in imagens)
        altura_maxima = max(img.height for img in imagens)

        # Cria a imagem de base (a "tela" da tirinha)
        tirinha = Image.new('RGB', (largura_total, altura_maxima))

        # Cola cada frame na tirinha
        posicao_x_atual = 0
        for img in imagens:
            tirinha.paste(img, (posicao_x_atual, 0))
            posicao_x_atual += img.width
            img.close() # Libera memória

        # Salva a imagem final
        tirinha.save(caminho_tirinha)
        print(f"INFO: Tirinha salva com sucesso em '{caminho_tirinha}'.")

    except FileNotFoundError:
        print(f"ERRO: Pasta de frames '{pasta_frames}' não encontrada.")
    except Exception as e:
        print(f"ERRO: Falha ao criar a tirinha de imagens: {e}")

# --- Orquestrador Principal ---

def main():
    """
    Função principal que orquestra todo o processo.
    """
    parser = argparse.ArgumentParser(
        description="Processador de Vídeo: Extrai frames, transcreve áudio e cria uma tirinha de imagens.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "caminho_video",
        help="O caminho completo para o arquivo de vídeo a ser processado."
    )
    args = parser.parse_args()
    caminho_video = args.caminho_video

    # 1. Validação inicial e criação do diretório de saída
    if not os.path.isfile(caminho_video):
        print(f"ERRO CRÍTICO: O arquivo especificado não existe ou não é um arquivo válido: '{caminho_video}'")
        sys.exit(1) # Encerra o script com código de erro

    nome_base_video = os.path.splitext(os.path.basename(caminho_video))[0]
    pasta_saida = os.path.join(os.path.dirname(caminho_video) or '.', nome_base_video)

    try:
        os.makedirs(pasta_saida, exist_ok=True)
        print(f"INFO: Diretório de saída criado/encontrado em: '{pasta_saida}'")
    except OSError as e:
        print(f"ERRO CRÍTICO: Não foi possível criar o diretório de saída '{pasta_saida}': {e}")
        sys.exit(1)


    # 2. Execução das tarefas
    try:
        # Extração de Frames
        num_frames = extrair_frames(caminho_video, pasta_saida, FRAMES_POR_SEGUNDO)

        # Transcrição de Áudio
        transcrever_audio(caminho_video, pasta_saida)

        # Criação da Tirinha
        if num_frames > 0:
            criar_tirinha(pasta_saida, pasta_saida)
        else:
            print("AVISO: Nenhuma imagem de frame foi gerada, pulando a criação da tirinha.")

        print("\n========================================================")
        print("✅ Processo concluído com sucesso!")
        print(f"👉 Todos os arquivos foram salvos em: {os.path.abspath(pasta_saida)}")
        print("========================================================")

    except Exception as e:
        print("\n========================================================")
        print(f"❌ Ocorreu um erro fatal durante a execução: {e}")
        print("========================================================")
        sys.exit(1)


if __name__ == "__main__":
    main()