# batch_processor.py
import argparse
import pandas as pd
import subprocess
import sys
from pathlib import Path

def main():
    """
    Função principal para analisar argumentos e rodar o processamento em lote.
    """
    parser = argparse.ArgumentParser(
        description="Processa em lote uma lista de vídeos do YouTube de um arquivo Excel ou CSV usando yt_cutter.py.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Exemplo de Uso:
  # Usando um arquivo Excel
  python batch_processor.py "caminho/para/sua/lista_videos.xlsx" --output-path "./videos_baixados"

O arquivo de entrada deve conter um cabeçalho com as seguintes colunas:
- url (Obrigatório): A URL completa do vídeo do YouTube.
- nome_do_arquivo (Recomendado): O nome desejado para o arquivo de saída.
- start_time (Opcional): O tempo de início para o corte (formato HH:MM:SS).
- end_time (Opcional): O tempo de fim para o corte (formato HH:MM:SS).
"""
    )

    parser.add_argument(
        "input_file",
        help="Caminho para o arquivo Excel (.xlsx) ou CSV (.csv) contendo a lista de vídeos."
    )
    parser.add_argument(
        "--output-path",
        required=True,
        help="O diretório global onde todos os vídeos e arquivos de log serão salvos."
    )

    args = parser.parse_args()

    input_path = Path(args.input_file)
    output_path = Path(args.output_path)
    # Garanta que o script yt_cutter.py esteja no mesmo diretório ou forneça o caminho correto
    tool_script_path = Path("downloads/youtube_processor.py")
    
    # --- 1. Validações ---
    if not input_path.exists():
        print(f"❌ Erro: O arquivo de entrada especificado não foi encontrado em '{input_path}'", file=sys.stderr)
        sys.exit(1)

    if not tool_script_path.exists():
        print(f"❌ Erro: O script '{tool_script_path}' não foi encontrado. Coloque-o no mesmo diretório.", file=sys.stderr)
        sys.exit(1)
        
    output_path.mkdir(parents=True, exist_ok=True)

    # --- 2. Ler Arquivo de Entrada ---
    try:
        print(f"📄 Lendo vídeos de '{input_path}'...")
        if input_path.suffix.lower() == '.xlsx':
            df = pd.read_excel(input_path, engine='openpyxl')
        elif input_path.suffix.lower() == '.csv':
            df = pd.read_csv(input_path)
        else:
            print(f"❌ Erro: Tipo de arquivo não suportado '{input_path.suffix}'. Use .xlsx ou .csv.", file=sys.stderr)
            sys.exit(1)
        
        if 'url' not in df.columns:
            print("❌ Erro: O arquivo de entrada deve conter uma coluna chamada 'url'.", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Erro: Falha ao ler ou processar o arquivo de entrada. Motivo: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ Encontrados {len(df)} vídeos para processar.")

    # --- 3. Iterar e Executar Subprocesso ---
    execution_logs = [] # Lista para armazenar os logs de execução
    
    for index, row in df.iterrows():
        video_number = index + 1
        
        # Obter dados da linha, tratando valores ausentes (NaN)
        url = row.get('url')
        file_name = row.get('id')
        start_time = row.get('start_time')
        end_time = row.get('end_time')

        print("\n" + "="*60)
        print(f"▶️ Processando vídeo {video_number} de {len(df)} | URL: {url}")
        print("="*60)

        if pd.isna(url):
            print("⚠️ Aviso: Pulando linha porque a 'url' está vazia.")
            execution_logs.append({'video_number': video_number, 'url': '', 'status': 'Skipped', 'details': 'URL was empty'})
            continue

        # Monta o comando para chamar o yt_cutter.py
        command = [
            sys.executable, str(tool_script_path), str(url),
            "--path", str(output_path),
            "--log-file", str(output_path / "yt_cutter_metadata_log.xlsx")
        ]

        if pd.notna(file_name):
            command.extend(["--name", str(file_name)])
        if pd.notna(start_time):
            # Converte para string para garantir o formato correto
            command.extend(["--start", str(start_time)])
        if pd.notna(end_time):
            command.extend(["--end", str(end_time)])

        log_entry = {'video_number': video_number, 'url': url, 'command': ' '.join(command)}

        try:
            print(f"🚀 Executando...")
            result = subprocess.run(
                command, check=True, capture_output=True, text=True, encoding='utf-8'
            )
            print("✅ Sucesso no processamento do vídeo.")
            print("--- Saída do yt_cutter.py ---")
            print(result.stdout)
            
            log_entry['status'] = 'Success'
            log_entry['details'] = result.stdout.strip().split('\n')[-1] # Pega a última linha do log de sucesso

        except subprocess.CalledProcessError as e:
            print("\n❌ Ocorreu um erro ao processar este vídeo.", file=sys.stderr)
            print("--- Saída de Erro do yt_cutter.py ---", file=sys.stderr)
            print(e.stderr, file=sys.stderr)
            
            log_entry['status'] = 'Failure'
            log_entry['details'] = e.stderr.strip().split('\n')[-1] # Pega a última linha do log de erro
        
        execution_logs.append(log_entry)

    # --- 4. Salvar Log de Execução ---
    log_file_path = output_path / "batch_execution_log.xlsx"
    print("\n" + "="*60)
    print(f"💾 Salvando log de execução em lote para '{log_file_path}'")
    log_df = pd.DataFrame(execution_logs)
    log_df.to_excel(log_file_path, index=False, engine='openpyxl')

    print("🎉 Processamento em lote concluído!")
    print(f"🎉 Todos os arquivos foram salvos em: '{output_path}'")
    print("="*60)


if __name__ == "__main__":
    main()
    
    