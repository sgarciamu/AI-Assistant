import requests
import json
import speech_recognition as sr
from gtts import gTTS
import pygame
import pyaudio
import os
import sys


def select_microphone():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    selected_device_index = None

    print("[i] Dispositivos de entrada de audio disponibles:\n")
    for i in range(0, numdevices):
        if p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
            device_name = p.get_device_info_by_host_api_device_index(0, i).get('name')
            print(f"Índice: {i} - Nombre: {device_name}")

            if selected_device_index is None:
                selected_device_index = i

    if selected_device_index is not None:
        selected_device_index = input("\n [?] Selecciona el índice del dispositivo de entrada de audio: ")
        try:
            selected_device_index = int(selected_device_index)
            if selected_device_index < 0 or selected_device_index >= numdevices:
                raise ValueError()
        except ValueError:
            print("[!] El índice introducido no es válido.")
            return None

        print(f"\n [i] Seleccionado el índice de dispositivo: {selected_device_index}\n")
        return selected_device_index
    else:
        print("\n[*] No se encontraron dispositivos de entrada de audio.")
        return None

def transcribe_audio(device_index):
    r = sr.Recognizer()
    with sr.Microphone(device_index=device_index) as source:
        print("Hable ahora...")
        audio = r.listen(source, timeout=5, phrase_time_limit=15)
        try:
            text = r.recognize_google(audio, language="es-ES")
            print("Usted dijo: {}".format(text))
            return text
        except sr.UnknownValueError:
            print("Lo siento, no pude entender lo que dijo.")
        except sr.RequestError as e:
            print(f"Lo siento, hubo un error al realizar la solicitud: {e}")
        except Exception as e:
            print(f"Se produjo un error inesperado: {e}")

def text_to_speech(text, filename):
    tts = gTTS(text=text, lang='es', slow=False)
    tts.save(filename)
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def chat_completions(input_text, temperature):

    api_key = os.environ.get('API_KEY')
    if api_key is None:
        print("La variable de entorno API_KEY no está definida.")
        print("Por favor, define la variable de entorno con el siguiente comando: ")
        print("export API_KEY='tu_api_key_aqui'")
        sys.exit()
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": input_text,
        "temperature": temperature,
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        data=json.dumps(data),
    )
    response_json = response.json()
    response_text = response_json['choices'][0]['message']['content']
    return response_text 

def leer_pregunta(texto):
    
    user_message = {"role": "user", "content": texto}
    print("\n")
    return user_message

if __name__ == "__main__":
    print("\nBienvenido al asistente de voz. que necesitas.\n")
    conversation_history = [{"role": "system", "content": "You are a helpful assistant."}]
    selected_device_index = select_microphone()
    if selected_device_index is not None:
      while True:
        input_text = transcribe_audio(selected_device_index)
        if input_text is not None:
            user_message = leer_pregunta(input_text)
            conversation_history.append(user_message)
            response = chat_completions(conversation_history, 0.7)
            if response:
                print(f"{response}")
                print("\n")   
                assistant_message = {"role": "assistant", "content": response}
                conversation_history.append(assistant_message)
                text_to_speech(response, "response.mp3")
            else:
                print("La respuesta de ChatGPT está vacía.")
                text_to_speech("La respuesta de ChatGPT está vacía.", "response.mp3")
        else:
            print("Por favor, intente hablar de nuevo.")
            text_to_speech("Por favor, intente hablar de nuevo.", "response.mp3")