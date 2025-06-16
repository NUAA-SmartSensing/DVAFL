import numpy as np
from sklearn.datasets import fetch_california_housing
from sklearn.preprocessing import StandardScaler
from torch.utils.data import Dataset
import torch

from dataset.BaseDataset import BaseDataset


class CaliforniaHousingDataset(Dataset):
    def __init__(self, features, targets, transform=None):
        self.data = features
        self.targets = targets
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        feature = self.data[idx]
        target = self.targets[idx]

        # 转换为tensor
        feature = torch.FloatTensor(feature)
        target = torch.FloatTensor([target])

        if self.transform:
            feature = self.transform(feature)

        return feature, target


class CaliforniaHousing(BaseDataset):
    def __init__(self, clients, iid_config, params):
        BaseDataset.__init__(self, iid_config)

        # 加载California Housing数据集
        housing = fetch_california_housing()
        X, y = housing.data, housing.target

        # 特征标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # 划分训练集和测试集
        # 使用前80%的数据作为训练集，后20%作为测试集
        split_idx = int(0.8 * len(X_scaled))

        X_train, X_test = X_scaled[:split_idx], X_scaled[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        # 创建数据集实例
        self.train_dataset = CaliforniaHousingDataset(X_train, y_train)
        self.test_dataset = CaliforniaHousingDataset(X_test, y_test)

        # 初始化数据分布
        self.init(clients, self.train_dataset, self.test_dataset)
