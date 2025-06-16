import torch.nn as nn
import torch.nn.functional as F


class MLPR(nn.Module):
    """
    多层感知机用于回归任务
    适用于 California Housing 数据集
    """
    def __init__(self, input_dim=8, hidden_dims=[64, 32], output_dim=1):
        super().__init__()

        # 输入层 -> 第一个隐藏层
        self.fc1 = nn.Linear(input_dim, hidden_dims[0])

        # 中间隐藏层
        self.hidden_layers = nn.ModuleList()
        for i in range(len(hidden_dims) - 1):
            self.hidden_layers.append(nn.Linear(hidden_dims[i], hidden_dims[i+1]))

        # 最后一个隐藏层 -> 输出层
        self.fc_out = nn.Linear(hidden_dims[-1], output_dim)

        # Dropout 层用于减少过拟合
        self.dropout = nn.Dropout(0.2)

    def forward(self, x):
        # 输入层 -> 第一个隐藏层
        x = F.relu(self.fc1(x))
        x = self.dropout(x)

        # 中间隐藏层
        for layer in self.hidden_layers:
            x = F.relu(layer(x))
            x = self.dropout(x)

        # 最后一个隐藏层 -> 输出层
        # 回归问题不使用激活函数
        x = self.fc_out(x)

        return x
