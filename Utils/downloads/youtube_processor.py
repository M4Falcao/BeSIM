# yt_cutter.py
# Versão Final: Script robusto para baixar, cortar e registrar vídeos do YouTube.

import argparse
import os
import re
import sys
import tempfile
import logging
import pandas as pd
from datetime import datetime
from yt_dlp import YoutubeDL
from moviepy import VideoFileClip
import subprocess

# --- Configuração do Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Funções Auxiliares ---

def parse_time_to_seconds(time_str: str) -> int:
    """Converte uma string 'HH:MM:SS' ou 'MM:SS' para segundos."""
    try:
        parts = list(map(int, time_str.split(':')))
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:
            return parts[0] * 60 + parts[1]
        else:
            raise ValueError("Formato de tempo inválido.")
    except (ValueError, IndexError):
        raise ValueError(f"Formato de timestamp inválido: '{time_str}'. Use 'HH:MM:SS' ou 'MM:SS'.")

def sanitize_filename(filename: str) -> str:
    """Remove caracteres inválidos de uma string para torná-la um nome de arquivo válido."""
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    sanitized = sanitized.replace(" ", "_")
    return sanitized[:150]

def format_seconds_to_time_string(seconds: float) -> str:
    """Converte segundos totais em uma string 'HH:MM:SS'."""
    if seconds is None:
        return "00:00:00"
    seconds = round(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def check_ffmpeg():
    """Verifica se o FFmpeg está disponível no sistema."""
    try:
        # Usamos o módulo nativo 'subprocess' para uma verificação mais robusta e compatível.
        # subprocess.DEVNULL oculta a saída do console de forma eficiente.
        # 'check=True' fará com que uma exceção seja levantada se o comando falhar.
        subprocess.run(
            ['ffmpeg', '-version'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        logging.info("Verificação do FFmpeg bem-sucedida.")
    except (FileNotFoundError, subprocess.CalledProcessError):
        # Capturamos FileNotFoundError se 'ffmpeg' não existir,
        # ou CalledProcessError se o comando retornar um erro.
        logging.error("FFMPEG não está instalado ou não foi encontrado no PATH do seu sistema.")
        logging.error("Por favor, siga os passos de instalação para o seu sistema operacional (conda ou sistema).")
        sys.exit(1)

def log_to_excel(log_data: dict, log_file: str):
    """Adiciona uma nova linha de metadados de vídeo ao arquivo Excel especificado."""
    try:
        log_header_pt = {
            'final_filename': 'Nome do Arquivo Salvo',
            'video_url': 'URL do Vídeo',
            'title': 'Título no YouTube',
            'duration': 'Duração (segundos)',
            'duration_string': 'Duração (HH:MM:SS)',
            'upload_date': 'Data de Publicação',
            'tags': 'Tags',
            'categories': 'Categorias'
        }
        df_new_row = pd.DataFrame([log_data])

        if not os.path.exists(log_file):
            logging.info(f"Arquivo de log '{log_file}' não encontrado. Criando...")
            df_new_row.rename(columns=log_header_pt).to_excel(log_file, index=False, engine='openpyxl')
        else:
            with pd.ExcelWriter(log_file, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                workbook = writer.book
                sheet_name = next(iter(writer.sheets))
                worksheet = writer.sheets[sheet_name]
                start_row = worksheet.max_row
                df_new_row.to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=False, header=False)
        logging.info(f"Metadados registrados com sucesso em '{log_file}'")
    except Exception as e:
        logging.error(f"Falha ao registrar dados no arquivo Excel: {e}")

# --- Função Principal de Processamento ---

def process_video(
    video_url: str,
    start_time: str = None,
    end_time: str = None,
    output_path: str = ".",
    output_name: str = None,
    log_file: str = 'download_log.xlsx'
):
    """Função principal para baixar, cortar, salvar e registrar o vídeo do YouTube."""
    if start_time:
        check_ffmpeg()

    try:
        logging.info("Buscando informações do vídeo...")
        with YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(video_url, download=False)
            video_title = info.get('title', 'youtube_video')
            duration = info.get('duration', 0)
            duration_string = info.get('duration_string', '00:00:00')
            upload_date_str = info.get('upload_date')
            tags = info.get('tags', [])
            categories = info.get('categories', [])

        final_duration_seconds = duration
        final_duration_string = duration_string
        formatted_upload_date = (datetime.strptime(upload_date_str, '%Y%m%d').strftime('%Y-%m-%d') if upload_date_str else 'N/A')

        start_seconds = parse_time_to_seconds(start_time) if start_time else 0
        end_seconds = parse_time_to_seconds(end_time) if end_time else None

        if duration > 0:
            if start_seconds >= duration: raise ValueError("O tempo de início é após o fim do vídeo.")
            if end_seconds and end_seconds > duration:
                logging.warning("O tempo de fim é após a duração do vídeo. Cortando até o final.")
                end_seconds = duration
            if end_seconds and end_seconds <= start_seconds: raise ValueError("O tempo de fim deve ser maior que o tempo de início.")

        if not os.path.exists(output_path):
            logging.info(f"Diretório de saída '{output_path}' não encontrado. Criando...")
            os.makedirs(output_path, exist_ok=True)

        final_filename = f"{sanitize_filename(output_name or video_title)}.mp4"
        final_filepath = os.path.join(output_path, final_filename)

        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts_download = {'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]', 'outtmpl': os.path.join(tmpdir, 'full_video.%(ext)s'), 'merge_output_format': 'mp4'}
            logging.info(f"Iniciando o download de '{video_title}'...")
            with YoutubeDL(ydl_opts_download) as ydl: ydl.download([video_url])
            logging.info("Download completo.")

            downloaded_file_path = os.path.join(tmpdir, 'full_video.mp4')
            if not os.path.exists(downloaded_file_path):
                potential_files = [f for f in os.listdir(tmpdir) if f.startswith('full_video')]
                if not potential_files: raise FileNotFoundError("Arquivo de vídeo baixado não encontrado no diretório temporário.")
                downloaded_file_path = os.path.join(tmpdir, potential_files[0])

            if start_time:
                logging.info(f"Cortando vídeo de {start_time} para {end_time or 'o fim'}...")
                video_clip = None
                try:
                    video_clip = VideoFileClip(downloaded_file_path)
                    if not video_clip or video_clip.duration is None: raise IOError("Falha ao carregar o arquivo de vídeo com MoviePy. Pode estar corrompido.")
                    cut_video = video_clip.subclipped(start_seconds, end_seconds)
                    final_duration_seconds = cut_video.duration
                    final_duration_string = format_seconds_to_time_string(final_duration_seconds)
                    cut_video.write_videofile(final_filepath, codec='libx264', audio_codec='aac', logger='bar')
                    cut_video.close()
                finally:
                    if video_clip: video_clip.close()
            else:
                logging.info("Nenhum corte necessário. Movendo o arquivo para o destino final.")
                os.rename(downloaded_file_path, final_filepath)

        logging.info(f"✅ Sucesso! Vídeo salvo em: {final_filepath}")

        log_data = {
            'final_filename': final_filename, 'video_url': video_url, 'title': video_title,
            'duration': round(final_duration_seconds, 2), 'duration_string': final_duration_string,
            'upload_date': formatted_upload_date, 'tags': ', '.join(tags) if tags else 'N/A',
            'categories': ', '.join(categories) if categories else 'N/A'
        }
        log_to_excel(log_data, log_file)

    except (ValueError, IOError, FileNotFoundError) as e:
        logging.error(f"Erro de Processamento: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado durante o processamento do vídeo: {e}")
        sys.exit(1)

# --- Ponto de Entrada do Script ---

def main():
    """Analisa os argumentos da linha de comando e inicia o processamento do vídeo."""
    parser = argparse.ArgumentParser(
        description="Um script para baixar, cortar e registrar vídeos do YouTube.",
        epilog="Exemplo: python yt_cutter.py 'URL_DO_VIDEO' --start 00:01:10 --end 00:01:55"
    )
    # --- Argumentos Alterados ---
    parser.add_argument("url", type=str, help="A URL completa do vídeo do YouTube.")
    parser.add_argument("--start", dest="start_time", type=str, default=None, help="Tempo de início opcional para o corte. Formato: 'HH:MM:SS'.")
    parser.add_argument("--end", dest="end_time", type=str, default=None, help="Tempo de fim opcional para o corte. Formato: 'HH:MM:SS'.")
    # --- Argumentos existentes ---
    parser.add_argument("--path", dest="output_path", type=str, default=".", help="Diretório de saída opcional.")
    parser.add_argument("--name", dest="output_name", type=str, default=None, help="Nome opcional para o arquivo de saída (sem extensão).")
    parser.add_argument("--log-file", dest="log_file", type=str, default="download_log.xlsx", help="Nome do arquivo Excel para registro. Padrão: 'download_log.xlsx'.")

    args = parser.parse_args()

    # A chamada para process_video agora usa os argumentos nomeados diretamente
    process_video(args.url, args.start_time, args.end_time, args.output_path, args.output_name, args.log_file)

if __name__ == "__main__":
    main()