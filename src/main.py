import threading
from Conversation.conversation import start_conversation, interrupt_speech, stop_conversation

if __name__ == '__main__':
    threading.Thread(target=start_conversation).start()
    while True:
        input("Started")
        interrupt_speech()
        print("Interrupted")
