import os
import moviepy.editor as mp

import asyncio
import websockets
import wave
import json


def process_video(t_audio_clear, web_socket, pucket_size, t_video, t_audio):
    # Распознаём аудио-файл
    if t_audio != "" and not (t_audio is None):
        asyncio.run(send_audio_via_websocket(t_audio_clear, web_socket, int(pucket_size), t_audio))
    # Распознаём видео-файл
    if t_video != "" and not (t_video is None):
        asyncio.run(send_audio_via_websocket(t_audio_clear, web_socket, int(pucket_size), t_video))

# отправка в web-socket
async def send_audio_via_websocket(t_audio_clear, web_socket, pucket_size, fileName):
    folder_work = get_folder_result()
    audio_file = mp.AudioFileClip(fileName)
    fileName_input = folder_work + '/vrem.wav'
    audio_file.write_audiofile(fileName_input)
    async with websockets.connect(web_socket, ping_timeout=100, close_timeout=100) as websocket:
        # Открываем аудиофайл
        with wave.open(fileName_input, 'rb') as wav_file:
            params = wav_file.getparams()
            print(f"Отправляю WAV с параметрами: {params}")
            await websocket.send(json.dumps(params._asdict()))
            
            while chunk := wav_file.readframes(pucket_size):
                await websocket.send(chunk)
            if t_audio_clear == 'Да':
                await websocket.send("EOF_1")
            else:
                await websocket.send("EOF")

        await websocket.close()
    
    #os.rmdir(folder_work)
    #os.remove(fileName)
    #os.remove(fileName_input)
    


# gradio может быть одновремено запущен несколько раз
# для обеспечения уникальности будем сохранять результаты в отдельных каталогах (просто под номерами)
def get_folder_result():
    sf = 'tmp'
    if not os.path.exists(sf):
        os.mkdir(sf)
        
    i = 1
    while os.path.exists(sf + '/' + str(i)):
        i += 1
    sf = sf + '/' + str(i)
    os.mkdir(sf)
    
    return sf
    
    
    