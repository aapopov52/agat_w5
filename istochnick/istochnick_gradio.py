import gradio as gr
import istochnick_audio_send_byte


with gr.Blocks() as demo:
    with gr.Column(scale=2):
               
        t_audio_clear = gr.Radio(["Да", "Нет"],
                                       label="Очистатить запись от шума:")        
        t_web_socket = gr.Text("ws://localhost:8765", label="web-socket:")
        t_pucket_size = gr.Text("1000", label="пакет(байт):")
        t_video = gr.Video(sources=['upload'])
        t_audio = gr.Audio(type='filepath', sources=['upload'])
        btn = gr.Button(value="Отправить файл")

        btn.click(istochnick_audio_send_byte.process_video,
                  inputs=[t_audio_clear, t_web_socket, t_pucket_size, t_video, t_audio])#, outputs=[t_stenogr])

demo.launch(share=True)
