if __name__ == '__main__':
    import threading
    from Conversation.conversation import start_conversation, interrupt_speech, stop_conversation

    threading.Thread(target=start_conversation).start()
    while True:
        try:
            input()
            interrupt_speech()
            print("Interrupted")
        except KeyboardInterrupt:
            stop_conversation()
            break
