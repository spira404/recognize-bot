import os
import json
from pydub import AudioSegment
from vosk import Model, KaldiRecognizer

# replace model_path with yours
def ogg_to_text(ogg_bytes, model_path="vosk-model-small-ru-0.22"):
    model = Model(model_path)
    audio = AudioSegment.from_ogg(ogg_bytes)

    if audio.channels > 1:
        audio = audio.set_channels(1)

    if audio.frame_rate != 16000:
        audio = audio.set_frame_rate(16000)

    if audio.sample_width != 2:
        audio = audio.set_sample_width(2)

    raw_data = audio.raw_data
    sample_rate = audio.frame_rate

    recognizer = KaldiRecognizer(model, sample_rate)
    recognizer.SetWords(True)

    chunk_size = 4000
    results = []

    for i in range(0, len(raw_data), chunk_size):
        chunk = raw_data[i:i+chunk_size]
        if recognizer.AcceptWaveform(chunk):
            result = json.loads(recognizer.Result())
            results.append(result["text"])

    final_result = json.loads(recognizer.FinalResult())
    results.append(final_result["text"])

    outmsg = " ".join(results).strip()
    print(outmsg)
    return outmsg
