# import json
# import os
# from datasets import Dataset
# from transformers import AutoTokenizer, AutoModelForQuestionAnswering, TrainingArguments, Trainer
# from peft import get_peft_model, LoraConfig, TaskType

# DATA_PATH = "airflow/data/qa_train.json"
# MODEL_NAME = "distilbert-base-uncased"
# OUTPUT_DIR = "models/finetuned-lora"

# def load_data(path=DATA_PATH):
#     with open(path) as f:
#         data = json.load(f)
#     return Dataset.from_list(data)

# def tokenize(batch, tokenizer):
#     return tokenizer(batch["question"], batch["answer"], truncation=True, padding="max_length", max_length=384)

# def train():
#     dataset = load_data()
#     tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
#     model = AutoModelForQuestionAnswering.from_pretrained(MODEL_NAME)

#     dataset = dataset.map(lambda x: tokenize(x, tokenizer))

#     lora_config = LoraConfig(
#         task_type=TaskType.QUESTION_ANSWERING,
#         r=8,
#         lora_alpha=16,
#         lora_dropout=0.1,
#         inference_mode=False,
#     )
#     model = get_peft_model(model, lora_config)

#     args = TrainingArguments(
#         output_dir=OUTPUT_DIR,
#         per_device_train_batch_size=2,
#         num_train_epochs=2,
#         logging_steps=10,
#         save_strategy="epoch",
#         save_total_limit=1,
#     )

#     trainer = Trainer(model=model, args=args, train_dataset=dataset)
#     trainer.train()

#     model.save_pretrained(OUTPUT_DIR)
#     tokenizer.save_pretrained(OUTPUT_DIR)
#     print(f"✅ Fine-tuned model saved to {OUTPUT_DIR}")

# if __name__ == "__main__":
#     train()
