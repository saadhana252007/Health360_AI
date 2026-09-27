import torch
import torch.nn as nn


class MultimodalFusion(nn.Module):

    def __init__(
        self,
        skin_dim=1280,
        oral_dim=512,
        wound_dim=384,
        symptom_dim=10,
        patient_dim=25,
        hidden_dim=64,
        health_dim=7
    ):
        super().__init__()

        self.skin_projection = nn.Sequential(
            nn.Linear(skin_dim, hidden_dim),
            nn.ReLU()
        )

        self.oral_projection = nn.Sequential(
            nn.Linear(oral_dim, hidden_dim),
            nn.ReLU()
        )

        self.wound_projection = nn.Sequential(
            nn.Linear(wound_dim, hidden_dim),
            nn.ReLU()
        )

        self.symptom_projection = nn.Sequential(
            nn.Linear(symptom_dim, hidden_dim),
            nn.ReLU()
        )

        self.patient_projection = nn.Sequential(
            nn.Linear(patient_dim, hidden_dim),
            nn.ReLU()
        )

        self.gate = nn.Sequential(
            nn.Linear(hidden_dim * 5, hidden_dim * 5),
            nn.ReLU(),
            nn.Linear(hidden_dim * 5, 5),
            nn.Softmax(dim=1)
        )

        self.fusion = nn.Sequential(
            nn.Linear(hidden_dim * 5, hidden_dim * 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU()
        )

        self.health_head = nn.Linear(hidden_dim, health_dim)

        self.confidence_head = nn.Sequential(
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )

    def forward(
        self,
        skin,
        oral,
        wound,
        symptoms,
        patient,
        modality_mask
    ):
        skin_features = self.skin_projection(skin)
        oral_features = self.oral_projection(oral)
        wound_features = self.wound_projection(wound)
        symptom_features = self.symptom_projection(symptoms)
        patient_features = self.patient_projection(patient)

        features = torch.stack(
            [
                skin_features,
                oral_features,
                wound_features,
                symptom_features,
                patient_features
            ],
            dim=1
        )

        mask = modality_mask.unsqueeze(-1)

        features = features * mask

        flat_features = features.flatten(1)

        gates = self.gate(flat_features)

        gates = gates * modality_mask

        gate_sum = gates.sum(dim=1, keepdim=True).clamp_min(1e-6)

        gates = gates / gate_sum

        gated_features = features * gates.unsqueeze(-1)

        fused_input = gated_features.flatten(1)

        fused = self.fusion(fused_input)

        health_vector = torch.sigmoid(
            self.health_head(fused)
        )

        confidence = self.confidence_head(fused)

        completeness = modality_mask.mean(
            dim=1,
            keepdim=True
        )

        return {
            "health_vector": health_vector,
            "confidence": confidence,
            "completeness": completeness,
            "gates": gates
        }