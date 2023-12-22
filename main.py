
#------------------librerias---------------------------
import json,time,pyglet,vosk,pyaudio,os,subprocess,pyttsx3
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
tts = pyttsx3.init()
tts.setProperty('voice','HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ES-MX_SABINA_11.0')
voces = tts.getProperty('voices')
for voz in voces:
    print(voz.id)
    print(voz.name)

with open("str_orders.json") as file:
    phrases = json.load(file)

sfxfiles = os.listdir("sfx/")
sfxfiles = [sfxfile for sfxfile in sfxfiles if os.path.isfile(os.path.join("sfx/", sfxfile))]
sortfiles = natsorted(sfxfiles)

def sfx(id):       
    return "sfx/"+sortfiles[id]

Format = pyaudio.paInt16
Channels = 1
Rate = 16000
Chunk = 1024
Akeys = ['se balón','sabina']
sleep = True
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
            if input.strip().lower() in phrases:
                func = globals().get(phrases[input.strip().lower()])    #<-------- obtencion del comando
                func() # noqa ignorar este error
            else:
                Say("disculpe, no entendí eso")
        except:
            Say("el modulo de reconocimiento no entendió eso. inténtelo de nuevo")
            
        
#--------------------------
def Say(text):
    
    if os.path.exists("temp_speaker.mp3"):
        os.remove("temp_speaker.mp3")
    
    tts.save_to_file(text,"temp_speaker.mp3")
    tts.runAndWait()

    audio, samplerate = sf.read("temp_speaker.mp3")
    delay = int(0.03 * samplerate)
    atten = 0.8
    metal = np.zeros_like(audio)
    metal[delay:] += audio[:-delay] * atten
    ecospeak = audio + metal
    os.remove("temp_speaker.mp3")
    sf.write("temp_speaker.mp3",ecospeak,samplerate)

    speak = AudioSegment.from_file("temp_speaker.mp3")


    play(speak)
    playSFX(6)
    os.remove("temp_speaker.mp3")
#------------------------------
def playSFX(sfxid):
    try:
        playsfx = pyglet.media.load(sfx(sfxid))
        playsfx.play()
        playsfx.delete()
    except Exception as e:
        Say("Algo está fallando en los sistemas de audio. Generando reporte de errores en consola.")
        
        print(e)
#-----------------comandos ----------
def terminar_programa():
    global instance_active 
    Say("adios, cerrando programa")
    time.sleep(0.9)
    print("Fin del programa")
    instance_active = False

def bajar_volumen():
    result = subprocess.run('nircmd changesysvolume -6900')
    print(result)
    Say("listo, Operador.")

def subir_volumen():
    result = subprocess.run('nircmd changesysvolume 6900')
    print(result)
    Say("listo, Operador.")

def decir_algo_inteligente():
    Say("El la historia del Internet, se dicen demasiados mitos desde quién fue su primer usuario, hasta quién podría darle fin a esta gran invento. Sin embargo, si tenemos un dato curioso de Internet y certero, es sobre quién fue la primera persona en usar el correo electrónico y enviar un email, se trata de Raymond Samuel Tomlinson. El cual creó un sistema Arpanet, para enviar correos entre dos usuarios diferentes, en una entrevista declaró que el mensaje de prueba era “QWERTYUIOP”.")
    

#---------------bucle-----------------
Say("iniciando sistemas")

while instance_active:
   main(Akeys)
   if sleep == False:
       listenUp(recognizer)

 