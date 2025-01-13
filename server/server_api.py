import os
import asyncio
import websockets
import wave
import json
import get_text_from_media

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

async def process_audio_async(clear_flag, filename):
    loop = asyncio.get_running_loop()
    return await asyncio.to_thread(get_text_from_media.get_text_from_video_audio, clear_flag, filename)

# WebSocket-сервер
async def server_handler(websocket):
    folder = get_folder_result()
    filename = folder + '/vrem.wav'
    b_audio_clear = 0            
    try:
        header_data = await asyncio.wait_for(websocket.recv(), timeout=10.0)
        params = json.loads(header_data) 
        
        with wave.open(filename, "wb") as wav_file:
            wav_file.setparams((params['nchannels'], params['sampwidth'], 
                                params['framerate'], params['nframes'], 
                                params['comptype'], params['compname']))
            
            # Получаем и записываем аудиоданные
            while True:
                data = await websocket.recv()
                if data == "EOF_1":
                    b_audio_clear = 1
                    break
                elif data == "EOF":
                    break
                
                wav_file.writeframes(data)
        print (filename)
        # распознаём текст
        
        sResult = await process_audio_async(b_audio_clear, filename)
        with open(folder + '/result.txt', "w") as file:
            file.write(sResult)     
                
    except Exception as e:
        print (websocket.send(f"Ошибка: {e}"))
    
    
# Асинхронная функция для запуска WebSocket-сервера
async def main():
    async with websockets.serve(server_handler, "localhost", 8765):  # Хост и порт
        print("WebSocket сервер запущен на ws://localhost:8765")
        await asyncio.Future()  # Блокируем текущую задачу (работаем до остановки сервера)

# Запуск основного цикла событий
asyncio.run(main())




