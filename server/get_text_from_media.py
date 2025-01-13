import os
import moviepy.editor as mp
from faster_whisper import WhisperModel
import nltk

# для чистки звука
from demucs import pretrained
from demucs.apply import apply_model
from demucs.audio import AudioFile, convert_audio
from pathlib import Path
import torch
import torchaudio


# МОДЕЛЬ РАСПОЗНАВАНИЯ
nltk.download('punkt')
nltk.download('stopwords')
whisper_model = WhisperModel("large-v2")

# МОДЕЛЬ УЛУЧШЕНИЯ ЗВУКА
# Устройство для вычислений: GPU или CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# Загрузка предобученной модели Demucs (например, htdemucs)
demucs_model_name = "htdemucs"
demucs_model = pretrained.get_model(demucs_model_name).to(device)
demucs_model.eval()
    
# Работа с аудио/видео на локальном диске
def get_text_from_video_audio(b_audio_clear, fileName_input):
    fileName_postobr = fileName_input
    if b_audio_clear == '1':
        fileName_postobr = clear_audio(fileName_input)
    segments, info = whisper_model.transcribe(fileName_postobr, 
        task='transcribe',  
        language="ru",
        beam_size=5,        # Настройка декодера (выражает количество гипотез для поиска)
        best_of=5           # Оставляем лучшую гипотезу из 5 вариантов)
       )
    sText = ''
    for segment in segments:
        sText += segment.text
    
    #os.remove(fileName_input)    пока не удаляем,чтобы посмотреть на файлы
    if fileName_postobr != fileName_input:
        os.remove(fileName_postobr)
    #os.rmdir(folder_work)
    
    return sText

# подавление шумов
def clear_audio (input_file):
    
    # Загрузка и конвертация аудиофайла
    wav = None
    #try:
    f = AudioFile(input_file)
    wav = f.read(streams=0)
    wav = convert_audio(wav, demucs_model.samplerate, demucs_model.samplerate, demucs_model.audio_channels)
    
    # Применение модели для разделения звуковых источников
    with torch.no_grad():
        sources = apply_model(demucs_model, wav[None], device=device)
        sources = sources[0]  # Убираем измерение batch
    
    # Сохранение всех дорожек (вокал, бас, ударные, и т.д.)
    # Нам интересен только вокал
    for source, name in zip(sources, demucs_model.sources):
        if name == 'vocals':
            output_file = os.path.dirname(input_file) + '/' + f"{Path(input_file).stem}_{name}.wav"
            torchaudio.save(str(output_file), source.cpu(), demucs_model.samplerate)
            return output_file
            #print(f"Сохранено: {output_file}")

    
    
    