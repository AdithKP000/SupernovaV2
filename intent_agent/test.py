from ml_agent import detect_intent

while True:
    q=input("You: ")
    print("Intent:",detect_intent(q))