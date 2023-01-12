import torch
from transformers import (AutoConfig, AutoModelForSequenceClassification,
                          AutoTokenizer, GPT2LMHeadModel, GPT2Tokenizer)
from config_loader import ConfigLoader

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class RecipeModel:
    def __init__(self, model_name: str, recipe_prefix=""):
        self.model_name = model_name
        self.config = AutoConfig.from_pretrained(model_name)

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.model = GPT2LMHeadModel.from_pretrained(
            model_name, config=self.config).to(DEVICE)

        self.input_ids = self.tokenizer.encode(
            f"[START]{recipe_prefix}", return_tensors="pt").to(DEVICE)
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

        generated_text = generated_text[generated_text.find(
            "[START]") + len("[START]"):generated_text.find("[END]")]
        return generated_text[:generated_text.rfind(".") + 1]


if __name__ == '__main__':
    cl = ConfigLoader()
    model_settings = cl.get_section("model_settings")
    recipe_prefix = model_settings["recipe_prefix"]
    model_name = model_settings["model_name"]
    rp = RecipeModel(model_name, recipe_prefix)
    print(rp.generate_recipe())
