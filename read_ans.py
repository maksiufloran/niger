import json

with open("questions.json", "r", encoding="utf-8") as f:
    quiz_history = json.load(f)

for item in quiz_history:
    print(f"[{item['timestamp']}] Pytanie: {item['question']}")
    for ans in item.get('allAnswers', []):
        status = "✅" if ans.get('isRight') else "❌"
        print(f"  {status} {ans.get('answers')}")
    print(item['analysis'])
    print("-" * 50)