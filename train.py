from transformers import Trainer, TrainingArguments
from datasets import Dataset
from transformers import DataCollatorForLanguageModeling
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from config_loader import ConfigLoader


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
    cl = ConfigLoader()
    train_settings = cl.get_section("train_settings")
    train_args = train_settings["train_args"]
    tokenizer_model_name = train_settings["tokenizer_model_name"]
    dataset_src = train_settings["dataset_src"]
    train_process(train_args, tokenizer_model_name, dataset_src)
