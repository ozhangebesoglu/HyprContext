import json

# Kaynak dosya: HYPRCONTEXT/history.jsonl
INPUT_FILE = "../history.jsonl"

# Çıkış dosyası: Eğitim/dataset.jsonl
OUTPUT_FILE = "dataset.jsonl"

entries = []

with open(INPUT_FILE, "r") as f:
    for line in f:
        data = json.loads(line.strip())
        
        item = {
            "instruction": "Kullanıcının ekran davranışını analiz et ve üretkenlik yorumunu üret.",
            "input": json.dumps(data, ensure_ascii=False),
            "output": data["summary"]
        }

        entries.append(item)

with open(OUTPUT_FILE, "w") as out:
    for e in entries:
        out.write(json.dumps(e, ensure_ascii=False) + "\n")

print("dataset.jsonl oluşturuldu ✔")
