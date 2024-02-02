import json
a=[]
with open("file.json") as f:
    score=json.load(f)
a.append(score)
print(a)
