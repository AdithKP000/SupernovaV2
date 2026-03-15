from qra import refourmulate_querry
from ../intent_agent/ml_agent import detect_intent

while True:
    query = input("Enter your query: ")
    intent = detect_intent(query)
    print(f"Intent: {intent}")
    rq= refourmulate_querry(query, intent)
    print(f"Reformulated Query: {rq}")