import torch
import os
import sys
import gc
from packaging import version
import transformers
from transformers import AutoModelForCausalLM, GemmaTokenizerFast, BitsAndBytesConfig
from trl import SFTTrainer, SFTConfig
from peft import LoraConfig
from datasets import load_dataset

# === BELLEK PARÇALANMASINI ÖNLEME ===
os.environ["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"

# === TEMİZLİK ===
gc.collect()
torch.cuda.empty_cache()

print(f"🔍 Transformers Sürümü: {transformers.__version__}")

# === MODEL AYARI ===
local_model_path = "/home/ozhan/gemma-2-2b-it" 
hub_model_id = "google/gemma-2-2b-it"

if not os.path.exists(local_model_path):
    print(f"❌ Model klasörü bulunamadı: {local_model_path}")
    exit()

print(f"🔄 Model yükleniyor: {local_model_path}...")

# === 4-bit QLoRA Config ===
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16
)

# === Tokenizer ===
try:
    print("🔤 Tokenizer internetten yükleniyor...")
    tokenizer = GemmaTokenizerFast.from_pretrained(hub_model_id)
    tokenizer.padding_side = "right"
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
except Exception as e:
    print(f"❌ Tokenizer hatası: {e}")
    exit()

# === Dataset ===
if not os.path.exists("dataset.jsonl"):
    print("❌ 'dataset.jsonl' yok!")
    exit()

dataset = load_dataset("json", data_files="dataset.jsonl")["train"]

def format_chat_template(example):
    return f"<start_of_turn>user\n{example['instruction']}\n\nVERİ:\n{example['input']}<end_of_turn>\n<start_of_turn>model\n{example['output']}<end_of_turn>"

dataset = dataset.map(lambda x: {"text": format_chat_template(x)}, batched=False)

# === LoRA Config (MİNİMUM AYARLAR) ===
lora_config = LoraConfig(
    r=4,
    lora_alpha=16,
    lora_dropout=0.05,
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "v_proj"] 
)

# === Model Yükleme ===
print("🧠 Model VRAM'e yükleniyor...")
model = AutoModelForCausalLM.from_pretrained(
    local_model_path,
    quantization_config=bnb_config,
    device_map="auto",
    attn_implementation="eager" 
)
model.config.use_cache = False

# === SFTConfig (ULTRA HAFİF) ===
training_args = SFTConfig(
    output_dir="ozhan-gemma-2b-lora",
    dataset_text_field="text",
    max_length=128,             # <-- 256'dan 128'e düştü (Büyük tasarruf)
    packing=False,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    gradient_checkpointing=True,
    gradient_checkpointing_kwargs={'use_reentrant': True}, # Bellek tasarrufu için True deniyoruz
    num_train_epochs=1,
    max_steps=50,
    learning_rate=2e-4,
    bf16=True,                      # <-- fp16 yerine bf16 (RTX 30 serisi için daha iyi)
    optim="paged_adamw_8bit",
    logging_steps=5,
    save_strategy="no",
    report_to="none"
)

# === Trainer ===
print("🚀 Eğitim başlıyor...")
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    peft_config=lora_config,
    args=training_args,
    processing_class=tokenizer 
)

# Son temizlik
torch.cuda.empty_cache()

trainer.train()

print("💾 Kaydediliyor...")
trainer.model.save_pretrained("ozhan-gemma-2b-lora")
tokenizer.save_pretrained("ozhan-gemma-2b-lora")
print("✔ Bitti!")