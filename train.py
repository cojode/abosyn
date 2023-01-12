from transformers import Trainer, TrainingArguments
from datasets import Dataset
from transformers import DataCollatorForLanguageModeling
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


def train_process(train_args: dict, model_name: str, dataset_src: str):
    # Устанавливаем сколько нейросети можно использовать видеопамяти
    torch.cuda.set_per_process_memory_fraction(1.0, 0)
    torch.cuda.empty_cache()

    torch.backends.cudnn.benchmark = True

    # Выбирается устройство - видеокарта если она доступна, или процессор
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Токенайзер берется из уже обученной нейронки,
    # он нужен для правильного составления тензоров
    tokenizer = AutoTokenizer.from_pretrained(
        model_name, bos_token="[START]", eos_token="[END]", pad_token='<pad>')
    tokenizer.save_pretrained("./tokenizer/")

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer, mlm=False)
    model = AutoModelForCausalLM.from_pretrained(model_name).to(DEVICE)
    model.resize_token_embeddings(len(tokenizer))

    # Данные с рецептами передаются в Dataset объект,
    # где с помощью токенайзера они преобразовываются в понятные для torch тензоры
    train_data = Dataset.from_text(dataset_src)
    train_data = train_data.map(lambda sample: tokenizer(sample["text"]))
    train_data.set_format(type="torch", columns=[
                          "input_ids", "attention_mask"])

    # Сам по себе процесс обучения нейросети очень затратный,
    # поэтому выбирается оптимизатор
    optimizer = torch.optim.Adagrad(model.parameters(), lr=0.001)

    # Конфигурации

    training_args = TrainingArguments(**train_args)

    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=train_data,
        optimizers=(optimizer, None)
    )

    trainer.train()


if __name__ == "__main__":
    train_args = {
        "output_dir": "RecipeModel",
        "overwrite_output_dir": True,
        "num_train_epochs": 10,
        "per_device_train_batch_size": 8,
        "per_device_eval_batch_size": 8,
        "gradient_accumulation_steps": 8,
        "warmup_steps": 0,
        "save_steps": 7230,
        "logging_steps": 20,
    }
    model_name = "sberbank-ai/rugpt3small_based_on_gpt2"
    dataset_src = "data/recipes.txt"
    train_process(train_args, model_name, dataset_src)
