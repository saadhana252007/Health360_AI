import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class SymptomModel:
    def __init__(self):
        self.model_name = "cristian-untaru/lora-biomedbert-medical-triage"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name
        )
        self.model.eval()

    def predict_text(self, text):
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        )

        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(
                outputs.logits,
                dim=-1
            )[0]

        index = int(torch.argmax(probabilities).item())

        return {
            "class_index": index,
            "class_name": self.model.config.id2label[index],
            "confidence": float(probabilities[index].item()),
            "probabilities": {
                self.model.config.id2label[i]: float(probabilities[i].item())
                for i in range(len(probabilities))
            }
        }