import os
import asyncio
from dotenv import load_dotenv
import google.generativeai as genai

async def main():
    """
    Função principal assíncrona para configurar e chamar a API Gemini.
    """
    # 1. Configuração da API (sintaxe moderna e mais segura)
    load_dotenv()
    api_key_google = os.getenv("API_GOOGLE")
    if not api_key_google:
        print("ERRO: Chave da API não encontrada na variável de ambiente 'API_GOOGLE'.")
        print("Verifique seu arquivo .env.")
        return

    genai.configure(api_key=api_key_google)

    # 2. Instanciando o modelo
    # Nota: 'gemini-2.5-pro-preview-06-05' pode ser um modelo de acesso restrito.
    # Usando 'gemini-1.5-pro-latest' que é o modelo público mais recente e poderoso.
    model_name = "gemini-1.5-pro-latest"
    model = genai.GenerativeModel(model_name)
    
    contents = "Explique como a IA funciona em poucas palavras"
    
    print(f"Enviando prompt para o modelo {model_name}...")

    # 3. Loop de tentativa e erro assíncrono
    while True:
        try:
            # 4. Chamada assíncrona para a API usando 'await'
            response = await model.generate_content_async(contents)
            
            print("\n--- Resposta do Gemini ---")
            print(response.text)
            print("--------------------------")
            break  # Sai do loop em caso de sucesso
            
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
            print("Tentando novamente em 1 segundo...")
            # 5. Pausa assíncrona para não bloquear o programa
            await asyncio.sleep(1)
            continue

if __name__ == "__main__":
    # 6. Ponto de entrada para executar o código assíncrono
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.")