import os
import time
import threading
import requests
import numpy as np
import scipy.io.wavfile as wavfile
import sounddevice as sd
import whisper
import pyttsx3
import tkinter as tk
from tkinter import ttk

# --- CONFIGURAÇÕES ORIGINAIS MANTIDAS ---
NOME_ASSISTENTE = "Denvers"
MODELO_LLM = "llama3.2:3b"  
IDIOMA = "pt"
TAXA_AMOSTRAGEM = 16000     
ARQUIVO_AUDIO = "temp_prompt.wav"

# Inicializa o motor de voz (TTS) local
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    if "brazil" in voice.name.lower() or "portuguese" in voice.name.lower() or "pt" in voice.id.lower():
        engine.setProperty('voice', voice.id)
        break
engine.setProperty('rate', 180) 

# Carrega o modelo Whisper local
print(f"🤖 Carregando modelo Whisper local para o {NOME_ASSISTENTE}...")
modelo_stt = whisper.load_model("tiny") 

def falar(texto):
    """Faz o computador falar e atualiza a interface."""
    atualizar_status(f"{NOME_ASSISTENTE}: {texto}")
    engine.say(texto)
    engine.runAndWait()

def perguntar_ollama(prompt_texto):
    """Envia o texto para o Ollama rodando localmente."""
    url = "http://localhost:11434/api/generate"
    system_prompt = f"Você é o {NOME_ASSISTENTE}, um assistente virtual prestativo. Responda sempre em português do Brasil de forma muito curta, direta e amigável."
    
    payload = {
        "model": MODELO_LLM,
        "prompt": f"{system_prompt}\n\nUsuário: {prompt_texto}\n{NOME_ASSISTENTE}:",
        "stream": False
    }
    try:
        resposta = requests.post(url, json=payload)
        if resposta.status_code == 200:
            return resposta.json().get("response", "")
        else:
            return "Erro ao me comunicar com o motor local da IA."
    except requests.exceptions.ConnectionError:
        return "Erro: O Ollama não está rodando. Inicie o Ollama primeiro."

# --- LOGICA DA INTERFACE GRAFICA ---
def atualizar_status(texto):
    """Atualiza o texto na janela principal com segurança de thread."""
    label_status.config(text=texto)
    root.update_idletasks()

def escutar_e_processar():
    """Roda em segundo plano para não travar a janela."""
    botao_ouvir.config(state=tk.DISABLED)
    
    duracao = int(slider_tempo.get())
    atualizar_status(f"🎤 Ouvindo por {duracao}s... Fale agora.")
    
    # Gravação
    audio_data = sd.rec(int(duracao * TAXA_AMOSTRAGEM), samplerate=TAXA_AMOSTRAGEM, channels=1, dtype='int16')
    sd.wait()
    wavfile.write(ARQUIVO_AUDIO, TAXA_AMOSTRAGEM, audio_data)
    
    # Transcrição
    atualizar_status("🧠 Processando áudio localmente...")
    resultado = modelo_stt.transcribe(ARQUIVO_AUDIO, language=IDIOMA)
    texto_usuario = resultado["text"].strip()
    
    if not texto_usuario:
        falar("Não entendi o que você disse. Pode repetir?")
        botao_ouvir.config(state=tk.NORMAL)
        return
        
    label_voce.config(text=f"Você disse: {texto_usuario}")
    
    # Resposta da IA
    resposta_ia = perguntar_ollama(texto_usuario)
    falar(resposta_ia)
    
    botao_ouvir.config(state=tk.NORMAL)

def iniciar_escuta():
    """Dispara a gravação em uma linha de execução separada."""
    threading.Thread(target=escutar_e_processar, daemon=True).start()

def boas_vindas_inicial():
    """Dá as boas-vindas logo após abrir a janela."""
    threading.Thread(target=lambda: falar(f"Olá! Eu sou o {NOME_ASSISTENTE}, seu assistente local. Como posso ajudar?"), daemon=True).start()

# --- DESIGN DA JANELA (Tkinter) ---
root = tk.Tk()
root.title(f"{NOME_ASSISTENTE} - Assistente de Voz Local")
root.geometry("450x350")
root.configure(bg="#1e1e2e")

# Estilo
style = ttk.Style()
style.theme_use('clam')

# Título
label_titulo = tk.Label(root, text=NOME_ASSISTENTE, font=("Helvetica", 24, "bold"), fg="#cba6f7", bg="#1e1e2e")
label_titulo.pack(pady=15)

# Status de Conversa
label_status = tk.Label(root, text="Inicializando...", font=("Helvetica", 11, "italic"), fg="#a6adc8", bg="#1e1e2e", wraplength=400)
label_status.pack(pady=10)

label_voce = tk.Label(root, text="", font=("Helvetica", 11), fg="#89b4fa", bg="#1e1e2e", wraplength=400)
label_voce.pack(pady=5)

# Ajuste de tempo de fala
label_tempo = tk.Label(root, text="Tempo de gravação (segundos):", font=("Helvetica", 10), fg="#cdd6f4", bg="#1e1e2e")
label_tempo.pack(pady=5)
slider_tempo = ttk.Scale(root, from_=3, to=15, value=5, orient=tk.HORIZONTAL)
slider_tempo.pack(pady=5, fill=tk.X, padx=100)

# Botão Principal para Falar
botao_ouvir = tk.Button(root, text="🎤 CLIQUE PARA FALAR", font=("Helvetica", 12, "bold"), fg="#11111b", bg="#a6e3a1", 
                        activebackground="#94e2d5", command=iniciar_escuta, padding=10, relief=tk.FLAT)
botao_ouvir.pack(pady=20)

# Inicia o cumprimento por voz assim que abrir
root.after(1000, boas_vindas_inicial)
root.mainloop()
