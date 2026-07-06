#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
河南本地化数据集处理模块
功能：加载、预处理和增强河南特色图像数据
"""

import os
import torch
from torchvision import transforms, datasets
from PIL import Image
import numpy as np

class HenanDataset:
    """河南本地化数据集处理类"""
    
    def __init__(self, base_dir='./henan_data'):
        self.base_dir = base_dir
        # 河南特色类别映射
        self.class_map = {
            0: '洛阳牡丹',
            1: '郑州商代青铜器', 
            2: '信阳毛尖茶树'
        }
    
    def create_transform(self):
        """创建数据预处理流程"""
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
    
    def load_dataset(self):
        """加载河南本地数据集"""
        try:
            # 检查数据集目录
            if not os.path.exists(self.base_dir):
                print(f"❌ 数据集目录不存在: {self.base_dir}")
                return None
            
            # 检查每个类别目录
            missing_classes = []
            for class_name in self.class_map.values():
                class_dir = os.path.join(self.base_dir, class_name)
                if not os.path.exists(class_dir):
                    missing_classes.append(class_name)
                    print(f"⚠️ 类别目录不存在: {class_dir}")
            
            if missing_classes:
                print(f"❌ 缺失以下类别目录: {missing_classes}")
                return None
            
            # 加载数据集
            transform = self.create_transform()
            full_dataset = datasets.ImageFolder(self.base_dir, transform=transform)
            
            # 筛选河南本地类别
            henan_indices = []
            for i, (img_path, label) in enumerate(full_dataset.imgs):
                if label in self.class_map:  # 只保留映射中的类别
                    henan_indices.append(i)
            
            if not henan_indices:
                print("❌ 未找到匹配的河南本地样本")
                return None
            
            print(f"✅ 数据集加载成功: {len(henan_indices)} 个样本")
            return torch.utils.data.Subset(full_dataset, henan_indices)
            
        except Exception as e:
            print(f"❌ 数据集加载错误: {e}")
            return None

# 测试代码
if __name__ == "__main__":
    # 测试数据集加载
    ds = HenanDataset()
    dataset = ds.load_dataset()
    
    if dataset is not None:
        print("✅ 数据集模块测试通过")
        print(f"支持类别: {list(ds.class_map.values())}")
    else:
        print("❌ 数据集模块测试失败")