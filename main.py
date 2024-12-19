
#------------------librerias---------------------------
import json,time,pyglet,pyaudio,os,subprocess,random,vosk, io
from gtts import gTTS
from google.cloud import texttospeech
from datetime import datetime
from pydub import AudioSegment
from pydub.playback import play
from natsort import natsorted
from unidecode import unidecode 
import speech_recognition as sr
import numpy as np
import soundfile as sf


#------------------------evento create-------------------
model = vosk.Model("models/vosk-model-small-es-0.42/")
vsk = vosk.KaldiRecognizer(model,16000)
recognizer=sr.Recognizer()
mic= sr.Microphone()
audio = pyaudio.PyAudio()
client = texttospeech.TextToSpeechClient.from_service_account_json("key.json")
voice = texttospeech.VoiceSelectionParams(
    language_code="es-MX", 
    ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL  # Género de la voz
)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16,  # Formato WAV (PCM)
    speaking_rate = 1.15,
    pitch = 0.60
)

with open("comandos.json") as file:
    phrases = json.load(file)

with open("dialogos.json") as file:
    dialogs = json.load(file)

with open("key.json") as file:
    key = json.load(file)

sfxfiles = os.listdir("sfx/")
sfxfiles = [sfxfile for sfxfile in sfxfiles if os.path.isfile(os.path.join("sfx/", sfxfile))]
sortfiles = natsorted(sfxfiles)

def sfx(id):
    return "sfx/"+sortfiles[id]

Format = pyaudio.paInt16
Channels = 1
Rate = 16000
Chunk = 1024
Akeys = ['astra','hasta','trump']
instance_active = True

#-------------main-----------------
def main(Akeys):
    print('sleeping...')
    listen = audio.open(format=Format,channels=Channels,rate=Rate,input=True,frames_per_buffer=Chunk)
    while True:
        data = listen.read(Chunk)
        if vsk.AcceptWaveform(data):
            resultado = vsk.Result()
            values = str(eval(resultado)['text']).lower()
            print(values)
            for word in Akeys:
                if  word in values:
                    listen.stop_stream()
                    listen.close()
                    print("Wake up!")
                    listenUp(recognizer)
                    break
            break
#-----------------funciones-----------------

def listenUp(recognizer):
    with mic as source:
        print("listening...")
        playSFX(6)
        audio = recognizer.listen(source)

        try: 
            inputraw = recognizer.recognize_google(audio,language='ES')

            print(inputraw)
            input = unidecode(inputraw)
            command = None

            for clave, valores in phrases.items():
                if input.strip().lower() in valores:
                    command = clave
                    break
            
            
            if command != None:
                func = globals().get(command)    #<-------- obtencion del comando
                func() # noqa ignorar este error
            else:
                Say("disculpe, no entendí eso")
        except Exception as e:
            print(e)
            import traceback
            traceback.print_exc()
            Say("el modulo de reconocimiento no entendió eso. inténtelo de nuevo")
            
        
#--------------------------
def Say(text):
    synthesis_input = texttospeech.SynthesisInput(text=text)
    start = time.time()
    response = client.synthesize_speech(
    input=synthesis_input, voice=voice, audio_config=audio_config)
    audio_file = io.BytesIO(response.audio_content)
    aud = AudioSegment.from_file(audio_file)
    temp_wav = io.BytesIO()
    aud.export(temp_wav,format="wav")
    samples, samplerate = sf.read(temp_wav)
    delay = int(0.02 * samplerate)#retraso del eco def 0.02
    atten = 0.80 ##ecos 0.80
    metal = np.zeros_like(samples)
    metal[delay:] += samples[:-delay] * atten
    ecospeak = samples + metal
    final_audio_file = io.BytesIO()
    sf.write(final_audio_file,ecospeak,samplerate,format="wav")
    final_audio_file.seek(0)
    speak = AudioSegment.from_file(final_audio_file)
    print(str(time.time()-start)+" ms")
    play(speak)
    playSFX(6)
    audio_file.seek(0)
    final_audio_file.seek(0)   
#------------------------------
def playSFX(sfxid):
    try:
        playsfx = pyglet.media.load(sfx(sfxid))
        playsfx.play()
    except Exception as e:
        Say("Algo está fallando en los sistemas de audio. Generando reporte de errores en consola.")
        
        print(e)
#-----------------comandos ----------
#-------------------------------------
#------------------------------------        
def terminar_programa():
    global instance_active 
    Say("adiós, Operador. apagando")
    time.sleep(0.9)
    print("Fin del programa")
    instance_active = False
#----------------------------
def bajar_volumen():
    result = subprocess.run('nircmd changesysvolume -6900')
    print(result)
    Say(random.choice(dialogs['afirmacion']))

def subir_volumen():
    result = subprocess.run('nircmd changesysvolume 6900')
    print(result)
    Say(random.choice(dialogs['afirmacion']))

def silenciar_volumen():
    result = subprocess.run('nircmd mutesysvolume 1')
    print(result)
    Say(random.choice(dialogs['afirmacion']))

def activar_volumen():
    result = subprocess.run('nircmd mutesysvolume 0')
    print(result)
    Say(random.choice(dialogs['afirmacion']))

def hora():
    hora = datetime.now().time()
    hour = hora.hour
    min = hora.minute
    if min == 0:
        min = "en punto"

    if hour > 11:
        if hour > 12:
            hour = hour - 12
        Say("Son las "+str(hour)+" "+str(min)+" p m")
    else:
        Say("Son las "+str(hour)+" "+str(min)+" a m")
def fecha():
    fecha = datetime.now()
    weekday = fecha.weekday()
    day = fecha.day
    month = fecha.month
    year = fecha.year

    weekname = ["Lunes ", "Martes ", "Miércoles ", "Jueves ", "Viernes ", "Sábado ", "Domingo "]
    monthname = ["Enero ","Febrero ","Marzo ","Abril ","Mayo ","Junio ","Julio ","Agosto ","Septiempre ","Octubre ","Noviembre ","Diciembre "]
    nowweekday = weekname[weekday]
    nowmonth = monthname[month-1]

    Say("hoy es "+ nowweekday + str(day)+" de "+ nowmonth+ "del "+ str(year) +" Operador")
#--------------------------------------
def decir_algo_inteligente():
    Say("¡Hola! Soy un asistente virtual creado para ayudarte. Hoy vamos a probar cómo se convierte este texto a voz utilizando la tecnología de síntesis de voz en español. La pronunciación y entonación son muy importantes para que el mensaje suene natural. La inteligencia artificial está mejorando cada día, y ahora puede generar voces muy realistas. ¡Es increíble cómo la tecnología avanza! Espero que este texto sea útil para realizar tu prueba.")
    

#---------------bucle-----------------
Say("Programa iniciado. escuchando...")

while instance_active:
    main(Akeys)