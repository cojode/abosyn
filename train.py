from transformers import Trainer, TrainingArguments
from datasets import Dataset
from transformers import DataCollatorForLanguageModeling
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os

# os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"
torch.cuda.set_per_process_memory_fraction(1.0, 0)

torch.cuda.empty_cache()
model_name = "sberbank-ai/rugpt3small_based_on_gpt2"
torch.backends.cudnn.benchmark = True

print(torch.cuda.is_available())
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

tokenizer = AutoTokenizer.from_pretrained(
    model_name, bos_token="[START]", eos_token="[END]", pad_token='<pad>')
tokenizer.save_pretrained("./tokenizer/")

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
model = AutoModelForCausalLM.from_pretrained(model_name).to(DEVICE)
model.resize_token_embeddings(len(tokenizer))

train_data = Dataset.from_text("data/recipes.txt")
train_data = train_data.map(lambda sample: tokenizer(sample["text"]))
train_data.set_format(type="torch", columns=["input_ids", "attention_mask"])

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

optimizer = torch.optim.Adagrad(model.parameters(), lr=0.001)


print(train_data[800])

training_args = TrainingArguments(
    output_dir="DescriptionGenerateModel",
    overwrite_output_dir=True,
    num_train_epochs=25,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    gradient_accumulation_steps=8,
    warmup_steps=0,
    save_steps=4950,
    logging_steps=5
)

trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=train_data,
    optimizers=(optimizer, None)
)

trainer.train()
