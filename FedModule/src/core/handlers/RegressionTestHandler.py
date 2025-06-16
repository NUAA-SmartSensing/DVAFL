import torch
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


def RegressionTest(test_dl, model, loss_func, dev, epoch, obj=None):
    """
    专门用于回归任务的测试函数，返回多种回归评估指标，而不是分类准确率
    """
    model.eval()
    test_loss = 0
    total_samples = 0
    all_outputs = []
    all_labels = []

    with torch.no_grad():
        for data in test_dl:
            inputs, labels = data
            inputs, labels = inputs.to(dev), labels.to(dev)
            outputs = model(inputs)

            # 收集所有预测值和真实值用于计算指标
            all_outputs.append(outputs.cpu().numpy())
            all_labels.append(labels.cpu().numpy())

            # 计算批次损失
            test_loss += loss_func(outputs, labels).detach().item()
            total_samples += labels.size(0)

    # 将收集的数据转换为numpy数组
    y_pred = np.vstack(all_outputs).reshape(-1)
    y_true = np.vstack(all_labels).reshape(-1)

    # 计算回归指标
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    # 平均损失
    loss = test_loss / len(test_dl)

    # 创建回归指标字典
    metrics_dict = {
        'mse': float(mse),
        'rmse': float(rmse),
        'mae': float(mae),
        'r2': float(r2),
        'total': float(r2) * 100  # 使用R²×100作为"准确率"指标，与系统兼容
    }

    print(f"Epoch {epoch} - MSE: {mse:.4f}, RMSE: {rmse:.4f}, MAE: {mae:.4f}, R²: {r2:.4f}")

    return metrics_dict, loss
