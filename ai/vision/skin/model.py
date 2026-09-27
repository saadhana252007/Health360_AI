import torch
import torch.nn as nn
import timm


class SkinModel(nn.Module):
    """
    EfficientNetV2-S based skin image classifier.

    Input:
        [batch, 3, 224, 224]

    Output:
        [batch, 11]
    """

    def __init__(self, num_classes=11, pretrained=False):
        super().__init__()

        self.num_classes = num_classes

        self.backbone = timm.create_model(
            "tf_efficientnetv2_s",
            pretrained=pretrained,
            num_classes=num_classes
        )

    def forward(self, x):
        return self.backbone(x)

    def get_embedding(self, x):
        """
        Returns the feature embedding before the final classifier.
        This will be useful later for multimodal fusion.
        """

        features = self.backbone.forward_features(x)

        # Global average pooling
        embedding = self.backbone.global_pool(features)

        # Flatten [B, C, 1, 1] -> [B, C]
        embedding = embedding.flatten(1)

        return embedding