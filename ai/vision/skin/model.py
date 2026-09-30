import json
import torch
import torch.nn as nn
from torchvision.models import efficientnet_b0
from huggingface_hub import hf_hub_download

class SkinModel(nn.Module):
    def __init__(self, num_classes=5, pretrained=False):
        super().__init__()

        self.class_names = [
            "Eczema / dermatitis",
            "Urticaria / allergic reaction",
            "Folliculitis / acne-like",
            "Psoriasis / papulosquamous",
            "Lesion - dermoscopic review recommended"
        ]

        self.backbone = efficientnet_b0(weights=None)
        self.backbone.classifier[1] = nn.Linear(
            self.backbone.classifier[1].in_features,
            5
        )

        checkpoint_path = hf_hub_download(
            repo_id="RevelaCap/clinical-skin-condition-v1",
            filename="best_model.pth"
        )

        checkpoint = torch.load(
        checkpoint_path,
        map_location="cpu",
        weights_only=True
        )

        self.backbone.load_state_dict(checkpoint["model_state_dict"])
        self.backbone.eval()

    def forward(self, x):
        return self.backbone(x)

    def get_embedding(self, x):
        features = self.backbone.features(x)
        features = self.backbone.avgpool(features)
        return torch.flatten(features, 1)

    def predict(self, x):
        with torch.no_grad():
            logits = self.forward(x)
            probabilities = torch.softmax(logits, dim=1)
            confidence, index = torch.max(probabilities, dim=1)

        return {
            "class_index": int(index.item()),
            "class_name": self.class_names[int(index.item())],
            "confidence": float(confidence.item()),
            "probabilities": {
                self.class_names[i]: float(probabilities[0][i].item())
                for i in range(len(self.class_names))
            }
        }