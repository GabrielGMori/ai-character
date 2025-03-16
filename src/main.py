if __name__ == '__main__':
    from Modules.Conversation.conversation import ConversationModule
    from Services.Input.speech_to_text import SpeechToText
    from output import OutputHandler
    import threading

    def on_stt_audio_received(author, text):
        response = conversation.send(author, text)
        if response is None:
            return
        elif response['audio']:
            output.play_audio_generator(response['audio'])

    def on_audio_stream_stop():
        conversation.unlock_outputting()

    conversation = ConversationModule(preset="Steve")
    stt = SpeechToText(author="Caéf", language=conversation.preset["language"], mic_index=1, on_audio_received=on_stt_audio_received)
    output = OutputHandler(device_index=5, on_audio_stream_stop=on_audio_stream_stop)

    threading.Thread(target=stt.start_listening, daemon=True).start()

    import pyaudio

    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    while True:
        try:
            prompt = input()
            conversation.interrupt_tts_stream()
            output.interrupt_playback()
        except KeyboardInterrupt:
            stt.stop_listening()
            conversation.interrupt_tts_stream()
            output.interrupt_playback()
            
            print("Finished program")
            break
