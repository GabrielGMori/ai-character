if __name__ == '__main__':
    from Modules.Conversation.conversation import ConversationModule
    from Services.Input.speech_to_text import SpeechToText
    import threading

    def on_stt_audio_received(author, text):
        conversation.send(author, text)

    conversation = ConversationModule(preset="Steve")
    stt = SpeechToText(author="Caéf", language=conversation.preset["language"], mic_index=1, on_audio_received=on_stt_audio_received)

    threading.Thread(target=stt.start_listening, daemon=True).start()

    while True:
        try:
            prompt = input()
            conversation.send("Caéf", prompt)
        except KeyboardInterrupt:
            stt.stop_listening()
            conversation.shutdown()
            executor = None
            break
    print("Finished program")
