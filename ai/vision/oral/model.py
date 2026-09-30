import torch
import torch.nn as nn
from torchvision.models import resnet50
from huggingface_hub import hf_hub_download


class OralModel(nn.Module):
    def __init__(self, num_classes=6, pretrained=False):
        super().__init__()

        checkpoint_path = hf_hub_download(
            repo_id="nsr51324/Oral_Diseases_Image_Classification",
            filename="checkpoints/best_model.pth"
        )

        checkpoint = torch.load(
            checkpoint_path,
            map_location="cpu",
            weights_only=True
        )

        self.class_names = checkpoint["class_names"]

        self.backbone = resnet50(weights=None)

        self.backbone.fc = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(
                self.backbone.fc.in_features,
                len(self.class_names)
            )
        )

        self.backbone.load_state_dict(checkpoint["state_dict"])
        self.backbone.eval()

    def forward(self, x):
        return self.backbone(x)

    def get_embedding(self, x):
        features = self.backbone.conv1(x)
        features = self.backbone.bn1(features)
        features = self.backbone.relu(features)
        features = self.backbone.maxpool(features)

        features = self.backbone.layer1(features)
        features = self.backbone.layer2(features)
        features = self.backbone.layer3(features)
        features = self.backbone.layer4(features)

        features = self.backbone.avgpool(features)

        return torch.flatten(features, 1)

    def predict(self, x):
        with torch.no_grad():
            logits = self.forward(x)
            probabilities = torch.softmax(logits, dim=1)
            confidence, index = torch.max(probabilities, dim=1)

        return {
            "class_index": int(index.item()),
            "class_name": self.class_names[index.item()],
            "confidence": float(confidence.item()),
            "probabilities": {
                self.class_names[i]: float(probabilities[0][i].item())
                for i in range(len(self.class_names))
            }
        }