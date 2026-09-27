import torch
import torch.nn as nn
import torchvision.models as models


class OralModel(nn.Module):
    """
    ResNet18 based oral image classifier.

    Input:
        [batch, 3, 224, 224]

    Output:
        [batch, 4]
    """

    def __init__(self, num_classes=4, pretrained=False):
        super().__init__()

        self.num_classes = num_classes

        self.backbone = models.resnet18(
            weights=None if not pretrained else models.ResNet18_Weights.DEFAULT
        )

        # Original ResNet18 classifier:
        # 512 features -> 1000 ImageNet classes
        #
        # Replace it with our 4 oral-health classes.
        self.backbone.fc = nn.Linear(
            self.backbone.fc.in_features,
            num_classes
        )

    def forward(self, x):
        return self.backbone(x)

    def get_embedding(self, x):
        """
        Extract the 512-dimensional feature representation
        before the final classification layer.
        """

        features = torch.flatten(
            self.backbone.avgpool(
                self.backbone.layer4(
                    self.backbone.layer3(
                        self.backbone.layer2(
                            self.backbone.layer1(
                                self.backbone.maxpool(
                                    self.backbone.relu(
                                        self.backbone.bn1(
                                            self.backbone.conv1(x)
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            ),
            1
        )

        return features