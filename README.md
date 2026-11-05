# 🤖 Denvers AI - Assistente de Voz 100% Local

O **Denvers** é um assistente virtual privado que roda inteiramente no seu computador. Ele escuta pelo microfone, processa os dados usando IA local e fala de volta em português brasileiro, garantindo total privacidade (sem enviar dados para a nuvem).

## 🛠️ Tecnologias Utilizadas
- **Interface:** Tkinter (Nativa do Python)
- **Cérebro (LLM):** Ollama (`llama3.2:3b`)
- **Audição (STT):** OpenAI Whisper (`tiny` executado localmente)
- **Fala (TTS):** Pyttsx3 (Sintetizador local do sistema)

## 🚀 Como Executar na Sua Máquina
1. Instale o [Ollama](https://ollama.com) e baixe o modelo no terminal:
   ```bash
   ollama run llama3.2:3b
   ```
2. Instale as dependências do projeto:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o aplicativo:
   ```bash
   python app.py
   ```
