import numpy as np
from scipy.io import wavfile
from pydub import AudioSegment

'''Generates pink noise'''
def generate_pink_noise(durationS, volumeNoise, samplingRate):
    numberOfSamples = int(durationS * samplingRate)
    whiteNoise = np.random.normal(0, 1, numberOfSamples)
    
    # filter
    b = np.array([0.02109238, 0.07113478, 0.68873558, 1.])
    a = np.array([1., -2.49495602, 2.017265875, -0.5221894])
    pinkNoise = np.zeros(numberOfSamples)
    for i in range(4, len(pinkNoise)):
        pinkNoise[i] = b[0] * whiteNoise[i] + b[1] * whiteNoise[i - 1] + b[2] * whiteNoise[i - 2] + b[3] * whiteNoise[i - 3] \
                        - a[1] * pinkNoise[i - 1] - a[2] * pinkNoise[i - 2] - a[3] * pinkNoise[i - 3]
    
    pinkNoise = pinkNoise / np.max(np.abs(pinkNoise))
    pinkNoise = pinkNoise * volumeNoise
    return pinkNoise

'''Generates a cosine tone'''
def generate_tone(frequency, volume, duration, samplingRate):
    t = np.linspace(0, duration, int(duration * samplingRate), False)
    sine = volume * np.cos(2 * np.pi * frequency * t)
    return sine

'''Applies fading in and out'''
def apply_fading(data, pauseStartS, pauseEndS, fadeInDurrationS, fadeOutDurrationS, samplingRate):
    numberOfSamples = len(data)
    numberOfPauseStartSamples = int(pauseStartS * samplingRate)
    numberOfPauseEndSamples = int(pauseEndS * samplingRate)
    numberOfFadeInSamples = int(fadeInDurrationS * samplingRate)
    numberOfFadeOutSamples = int(fadeOutDurrationS * samplingRate)

    pauseStart = np.linspace(0, 0, numberOfPauseStartSamples)
    fadeIn = np.linspace(0, 1, numberOfFadeInSamples)
    noFade = np.linspace(1,1,numberOfSamples-numberOfFadeInSamples-numberOfFadeOutSamples-numberOfPauseStartSamples-numberOfPauseEndSamples)
    fadeOut = np.linspace(1, 0, numberOfFadeOutSamples)
    pauseEnd = np.linspace(0, 0, numberOfPauseEndSamples)

    fading = np.concatenate((pauseStart, fadeIn, noFade, fadeOut, pauseEnd))
    data *= fading
    return data

'''Saves audio file as .wav'''
def save_audio_file(fileName, data, samplingRate):
    wavFilename = fileName + ".wav"
    mp3Filename = fileName + ".mp3"
    wavfile.write(wavFilename, samplingRate, data)
    sound = AudioSegment.from_wav(wavFilename)
    sound.export(mp3Filename, format="mp3")

def main():
    #Parameters
    durationIn = 5
    durationOut = 10
    samplingRate = 44100
    fadeInDurationS = 2
    fadeOutDurationS = 1
    pauseStartS = 0.25
    pauseEndS = 0.25
    volumeTone = 0.2
    volumeNoise = 0.5
    audioDurationS = 10 * 60

    #Tone definitions
    C1 = 32.7032
    D1 = 36.7081
    E1 = 41.2034
    G1 = 48.9994

    #Inbreath sound generation
    pinkNoiseIn = generate_pink_noise(durationIn, volumeNoise, samplingRate) + generate_tone(pow(2,2) * G1, volumeTone, durationIn, samplingRate)
    pinkNoiseIn = apply_fading(pinkNoiseIn, pauseStartS, pauseEndS, fadeInDurationS, fadeOutDurationS, samplingRate)
    
    #Outbreath sound generation
    pinkNoiseOut = generate_pink_noise(durationOut, volumeNoise, samplingRate) + generate_tone(pow(2,2) * C1, volumeTone, durationOut, samplingRate)
    pinkNoiseOut = apply_fading(pinkNoiseOut, pauseStartS, pauseEndS, fadeInDurationS, fadeOutDurationS, samplingRate)
    
    #repetitions
    cycle = np.concatenate((pinkNoiseIn, pinkNoiseOut))
    numberOfCycles = int(audioDurationS / (durationIn + durationOut))
    cycles = np.zeros((0)) 
    for i in range(0, numberOfCycles):
       cycles = np.concatenate((cycles, cycle))
    
    #save file
    save_audio_file(str(durationIn) + "_" + str(durationOut), (cycles * 32767).astype(np.int16), samplingRate)

if __name__ == "__main__":
    import sys
    sys.path.append('/path/to/ffmpeg')

    main()