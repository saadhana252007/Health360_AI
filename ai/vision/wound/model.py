import torch
import torch.nn as nn
import segmentation_models_pytorch as smp


class WoundModel(nn.Module):
    """
    Wound analysis model.

    Performs:
    1. Wound segmentation
    2. Wound classification

    Input:
        [batch, 3, 224, 224]

    Segmentation output:
        [batch, 1, 224, 224]

    Classification output:
        [batch, 8]
    """

    def __init__(
        self,
        num_classes=8,
        encoder_name="timm-efficientnet-b3",
        pretrained=False
    ):
        super().__init__()

        self.num_classes = num_classes

        # --------------------------------------------------
        # 1. SEGMENTATION BRANCH
        # --------------------------------------------------

        self.segmentation_model = smp.Unet(
            encoder_name=encoder_name,
            encoder_weights="imagenet" if pretrained else None,
            in_channels=3,
            classes=1
        )

        # --------------------------------------------------
        # 2. CLASSIFICATION ENCODER
        # --------------------------------------------------

        self.classification_encoder = smp.encoders.get_encoder(
            encoder_name,
            in_channels=3,
            depth=5,
            weights="imagenet" if pretrained else None
        )

        # IMPORTANT:
        # Get the actual number of output channels
        # from the encoder instead of assuming it.
        encoder_channels = self.classification_encoder.out_channels[-1]

        print("Classification encoder output channels:", encoder_channels)

        # --------------------------------------------------
        # 3. CLASSIFICATION HEAD
        # --------------------------------------------------

        self.classification_head = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Dropout(0.2),
            nn.Linear(encoder_channels, num_classes)
        )

    def forward(self, x):

        # Segmentation branch
        segmentation_output = self.segmentation_model(x)

        # Classification branch
        features = self.classification_encoder(x)

        # Final encoder feature map
        classification_features = features[-1]

        # Classification prediction
        classification_output = self.classification_head(
            classification_features
        )

        return {
            "segmentation": segmentation_output,
            "classification": classification_output
        }

    def get_embedding(self, x):
        """
        Extract final encoder representation
        for future multimodal fusion.
        """

        features = self.classification_encoder(x)

        final_features = features[-1]

        # Global average pooling
        embedding = torch.mean(
            final_features,
            dim=(2, 3)
        )

        return embedding