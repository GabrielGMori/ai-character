if __name__ == '__main__':
    import threading
    from concurrent.futures import ThreadPoolExecutor
    from Conversation.conversation import ConversationModule

    conversation = ConversationModule()

    executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="Main")
    executor.submit(conversation.start_conversation)

    while True:
        try:
            input()
            conversation.interrupt_speech()
        except KeyboardInterrupt:
            conversation.interrupt_speech()
            conversation.stop_conversation()
            executor.shutdown()
            break
    print("Finished program")
