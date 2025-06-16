from torch import nn
from torchvision import models


class ResNet18Pre(nn.Module):
    def __init__(self, num_classes=10):
        super(ResNet18Pre, self).__init__()
        self.model = models.resnet18(pretrained=True)
        self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)

    def forward(self, x):
        return self.model(x)


class ResNet18ForOneTunnel(nn.Module):
    def __init__(self, num_classes=10, pretrained=False):
        super(ResNet18ForOneTunnel, self).__init__()
        self.model = models.resnet18(pretrained=pretrained)
        self.model.conv1 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)

    def forward(self, x):
        return self.model(x)


class ResNet18CIFAR10(nn.Module):
    """
    针对CIFAR-10优化的ResNet18：
    - 输入层卷积核由7x7改为3x3，步长由2改为1，padding由3改为1
    - 移除最大池化层（maxpool）
    - 保持后续结构不变
    """
    def __init__(self, num_classes=10):
        super(ResNet18CIFAR10, self).__init__()
        self.model = models.resnet18(pretrained=False)
        self.model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
        self.model.maxpool = nn.Identity()
        self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)

    def forward(self, x):
        return self.model(x)


class ResNet50CIFAR100(nn.Module):
    """
    针对CIFAR-100优化的ResNet50：
    - 输入层卷积核由7x7改为3x3，步长由2改为1，padding由3改为1
    - 移除最大池化层（maxpool）
    - 输出类别数为100
    - 可选是否加载预训练权重
    """
    def __init__(self, num_classes=100, pretrained=False):
        super(ResNet50CIFAR100, self).__init__()
        self.model = models.resnet50(pretrained=pretrained)
        self.model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
        self.model.maxpool = nn.Identity()
        self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)

    def forward(self, x):
        return self.model(x)
