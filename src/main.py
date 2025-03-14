if __name__ == '__main__':
    from concurrent.futures import ThreadPoolExecutor
    from Modules.Conversation.conversation import ConversationModule
    from Services.Input.speech_to_text import SpeechToText

    def on_stt_audio_received(author, text):
        conversation.send(author, text)

    conversation = ConversationModule(preset="Steve")
    stt = SpeechToText(author="Mori", language=conversation.preset["language"], mic_index=1, on_audio_received=on_stt_audio_received, )

    executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="Main")
    executor.submit(stt.start_listening)

    while True:
        try:
            input()
            conversation.interrupt_tts()
        except KeyboardInterrupt:
            conversation.interrupt_tts()
            stt.stop_listening()
            executor.shutdown()
            break
    print("Finished program")
