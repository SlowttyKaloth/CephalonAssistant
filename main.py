
#------------------librerias----------------------------
import json,time,pyglet,vosk,pyaudio,io,os,subprocess
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from natsort import natsorted
from unidecode import unidecode 
import speech_recognition as sr

#------------------------evento create-------------------
model = vosk.Model("models/vosk-model-small-es-0.42/")
vsk = vosk.KaldiRecognizer(model,16000)
recognizer=sr.Recognizer()
mic= sr.Microphone()
audio = pyaudio.PyAudio()

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
Akeys = ['se balón','ortiz']
sleep = True
instance_active = True

#-------------main-----------------
def main(sleep,Akeys):
    print('sleeping...')
    listen = audio.open(format=Format,channels=Channels,rate=Rate,input=True,frames_per_buffer=Chunk)
    while sleep:
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
                    sleep = False
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
    audioBuffer = io.BytesIO()
    speech = gTTS(text,lang='es-us',slow=False)
    if os.path.exists("temp_speaker.mp3"):
        os.remove("temp_speaker.mp3")
    
    with open("temp_speaker.mp3","wb") as file:
        audioBuffer.seek(0)
        speech.write_to_fp(file)
        audioBuffer.close()

    speak = AudioSegment.from_mp3("temp_speaker.mp3")
    speakup = speak.speedup(playback_speed =1.3)

    playSFX(6)
    time.sleep(0.7)
    play(speakup)
    playSFX(6)

    speak = None
    os.remove("temp_speaker.mp3")
#------------------------------
def playSFX(sfxid):
    try:
        playsfx = pyglet.media.load(sfx(sfxid))
        playsfx.play()
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
    

#---------------bucle-----------------
Say("iniciando sistema...")

while instance_active:
   main(sleep,Akeys)
   if sleep == False:
       listenUp(recognizer)

 