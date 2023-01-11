import torch
from transformers import (AutoConfig, AutoModelForSequenceClassification,
                          AutoTokenizer, GPT2LMHeadModel, GPT2Tokenizer)

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class RecipeModel:
    def __init__(self, model_name):
        self.model_name = model_name
        self.config = AutoConfig.from_pretrained(model_name)

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.model = GPT2LMHeadModel.from_pretrained(
            model_name, config=self.config).to(DEVICE)

        text = "[START]"
        self.input_ids = self.tokenizer.encode(
            text, return_tensors="pt").to(DEVICE)
        self.model.eval()

    def generate_recipe(self, max_length=1000):
        with torch.no_grad():
            out = self.model.generate(self.input_ids,
                                      do_sample=True,
                                      temperature=1.2,
                                      top_p=0.9,
                                      top_k=40,
                                      max_length=max_length)

        generated_text = list(map(self.tokenizer.decode, out))[0]

        return generated_text[generated_text.find("[START]") + len("[START]"):generated_text.find("[END]")]


def main():
    rp = RecipeModel("havai/awesome_recipes")
    print(rp.generate_recipe(max_length=1000))


if __name__ == '__main__':
    main()
