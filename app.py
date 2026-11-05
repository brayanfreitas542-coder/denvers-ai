import os
import time
import threading
import requests
import numpy as np
import scipy.io.wavfile as wavfile
import sounddevice as sd
import whisper
import pyttsx3
import customtkinter as ctk

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
    atualizar_status(f"{texto}")
    engine.say(texto)
    engine.runAndWait()

def perguntar_ollama(prompt_texto):
    """Envia o texto para o Ollama rodando localmente."""
    url = "http://localhost:11434/api/generate"
    system_prompt = f"Você é o {NOME_ASSISTENTE}, uma inteligência artificial sofisticada inspirada no JARVIS. Responda sempre em português do Brasil de forma curta, direta e com um tom elegante e prestativo."
    
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
            return "Erro nos sistemas centrais de IA."
    except requests.exceptions.ConnectionError:
        return "Erro: O Ollama não foi detectado em segundo plano."

# --- INTERFACE GRÁFICA ESTILO STARK INDUSTRIES ---
ctk.set_appearance_mode("dark")  # Modo Escuro Ativado
ctk.set_default_color_theme("blue")  # Tom de azul tecnológico

def atualizar_status(texto):
    label_status.configure(text=texto)
    root.update_idletasks()

def escutar_e_processar():
    botao_ouvir.configure(state="disabled", fg_color="#333333", text="SISTEMAS OCUPADOS")
    duracao = int(slider_tempo.get())
    
    # Efeito visual holográfico mudando as cores do núcleo
    frame_nucleo.configure(border_color="#ff0055") # Vermelho enquanto grava
    atualizar_status(f"🎤 GRAVANDO ÁUDIO LOCAL ({duracao}s)... FALER AGORA")
    
    audio_data = sd.rec(int(duracao * TAXA_AMOSTRAGEM), samplerate=TAXA_AMOSTRAGEM, channels=1, dtype='int16')
    sd.wait()
    wavfile.write(ARQUIVO_AUDIO, TAXA_AMOSTRAGEM, audio_data)
    
    frame_nucleo.configure(border_color="#1f538d") # Azul processando
    atualizar_status("🧠 PROCESSANDO DADOS VIA MATRIZ LOCAL...")
    
    resultado = modelo_stt.transcribe(ARQUIVO_AUDIO, language=IDIOMA)
    texto_usuario = resultado["text"].strip()
    
    if not texto_usuario:
        frame_nucleo.configure(border_color="#00f0ff")
        falar("Nenhum dado de voz foi capturado, Senhor. Poderia repetir?")
        botao_ouvir.configure(state="normal", fg_color="#00f0ff", text="ATIVAR MATRIZ DE VOZ")
        return
        
    label_voce.configure(text=f"Usuário: {texto_usuario}")
    
    resposta_ia = perguntar_ollama(texto_usuario)
    frame_nucleo.configure(border_color="#00f0ff") # Ciano padrão do Jarvis
    falar(resposta_ia)
    
    botao_ouvir.configure(state="normal", fg_color="#00f0ff", text="ATIVAR MATRIZ DE VOZ")

def iniciar_escuta():
    threading.Thread(target=escutar_e_processar, daemon=True).start()

def boas_vindas_inicial():
    threading.Thread(target=lambda: falar(f"Sistemas integrados, Senhor. Eu sou o {NOME_ASSISTENTE}. Matriz local online e pronta."), daemon=True).start()

# Janela Principal
root = ctk.CTk()
root.title(f"STARK INDUSTRIES - {NOME_ASSISTENTE} OS")
root.geometry("500x520")
root.resizable(False, False)

# Painel Centralizador (Visual Holograma)
frame_fundo = ctk.CTkFrame(root, fg_color="#0a0e14", corner_radius=0)
frame_fundo.pack(fill="both", expand=True)

# Título Estilo Display de Interface de Combate
label_titulo = ctk.CTkLabel(frame_fundo, text=f"🧬 {NOME_ASSISTENTE}.SYS v1.0", font=("Courier New", 26, "bold"), text_color="#00f0ff")
label_titulo.pack(pady=25)

# Elemento Central: O "Reator" / Núcleo do Jarvis
frame_nucleo = ctk.CTkFrame(frame_fundo, width=140, height=140, corner_radius=70, border_width=4, border_color="#00f0ff", fg_color="#0d1b2a")
frame_nucleo.pack(pady=10)
frame_nucleo.pack_propagate(False)

label_nucleo_txt = ctk.CTkLabel(frame_nucleo, text="CORE\nONLINE", font=("Courier New", 14, "bold"), text_color="#00f0ff")
label_nucleo_txt.place(relx=0.5, rely=0.5, anchor="center")

# Console de Status Geral (Onde aparecem as falas)
label_status = ctk.CTkLabel(frame_fundo, text="Inicializando protocolos...", font=("Consolas", 13), text_color="#a6adc8", wraplength=420)
label_status.pack(pady=20)

label_voce = ctk.CTkLabel(frame_fundo, text="", font=("Consolas", 13), text_color="#89b4fa", wraplength=420)
label_voce.pack(pady=5)

# Painel de controle inferior
label_tempo = ctk.CTkLabel(frame_fundo, text="JANELA DE CAPTURA (SEGUNDOS):", font=("Consolas", 11), text_color="#575f73")
label_tempo.pack(pady=2)
slider_tempo = ctk.CTkSlider(frame_fundo, from_=3, to=15, number_of_steps=12, width=250, button_color="#00f0ff", button_hover_color="#94e2d5")
slider_tempo.set(5)
slider_tempo.pack(pady=5)

# Botão Holográfico Principal
botao_ouvir = ctk.CTkButton(frame_fundo, text="ATIVAR MATRIZ DE VOZ", font=("Courier New", 14, "bold"), text_color="#0a0e14",
                            fg_color="#00f0ff", hover_color="#94e2d5", corner_radius=10, height=45, width=280, command=iniciar_escuta)
botao_ouvir.pack(pady=25)

root.after(1000, boas_vindas_inicial)
root.mainloop()

