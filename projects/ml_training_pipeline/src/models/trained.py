import torch
import torch.nn as nn
import torchvision.models as models

class TrainedHenanModel(nn.Module):
    """河南AI训练模型（与主程序兼容）"""
    
    def __init__(self, num_classes=3):
        super().__init__()
        self.base_model = models.resnet18(pretrained=False)
        self.base_model.fc = nn.Linear(self.base_model.fc.in_features, num_classes)
    
    def forward(self, x):
        return self.base_model(x)

# 兼容性别名
UltimateHenanCNN = TrainedHenanModel