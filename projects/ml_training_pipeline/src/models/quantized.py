#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
河南AI模型量化程序 - 完整版
功能：将训练好的FP32模型转换为INT8量化模型，减少模型大小并提升推理速度
版本：2.0 - 主程序兼容版
"""

import torch
import torch.nn as nn
import torch.quantization as quantization
import os
import time
from pathlib import Path

# =============================
# 1. 配置参数
# =============================
PROJECT_ROOT = Path(__file__).parent.absolute()
MODEL_DIR = PROJECT_ROOT / "model"
DATA_DIR = PROJECT_ROOT / "date"

# 量化配置
QUANTIZATION_CONFIG = {
    'dtype': torch.qint8,          # 量化数据类型
    'modules_to_quantize': {nn.Linear, nn.Conv2d},  # 要量化的层类型
    'quantization_type': 'dynamic' # 量化类型：动态量化
}

# =============================
# 2. 模型定义（与主程序保持一致）
# =============================
class UltimateHenanCNN(nn.Module):
    """
    河南AI模型定义 - 与训练代码完全一致
    确保权重形状兼容性：[64,3,3,3]卷积核和[3,512]全连接层
    """
    
    def __init__(self, num_classes=3):
        super().__init__()
        
        # 特征提取网络
        self.features = nn.Sequential(
            # 第一卷积层：3x3卷积核，匹配[64,3,3,3]权重
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),  # 224→112
            
            # 第二卷积层
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),  # 112→56
            
            # 第三卷积层
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),  # 56→28
            
            # 第四卷积层
            nn.Conv2d(256, 512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((1, 1))  # 全局平均池化
        )
        
        # 分类器 - 匹配[3,512]权重形状
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)  # 直接512→3，完全匹配权重
        )
    
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

# =============================
# 3. 核心量化函数
# =============================
def load_trained_model(model_path):
    """加载已训练的FP32模型"""
    print("🔍 加载训练模型...")
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型文件不存在: {model_path}")
    
    # 创建模型实例
    model = UltimateHenanCNN(num_classes=3)
    
    # 加载权重（非严格模式以处理轻微不匹配）
    state_dict = torch.load(model_path, map_location='cpu')
    
    # 权重兼容性处理
    model_state = model.state_dict()
    filtered_state = {k: v for k, v in state_dict.items() if k in model_state and v.shape == model_state[k].shape}
    
    if len(filtered_state) / len(model_state) < 0.9:
        print("⚠️ 权重兼容性较低，部分层将使用初始化值")
    
    model.load_state_dict(filtered_state, strict=False)
    model.eval()  # 设置为评估模式
    
    print(f"✅ 模型加载完成: {len(filtered_state)}/{len(model_state)}层权重匹配")
    return model

def apply_dynamic_quantization(model):
    """应用动态量化"""
    print("⚡ 应用动态量化...")
    
    # 配置量化参数
    quantization_config = quantization.QConfig(
        activation=quantization.default_observer,
        weight=quantization.default_per_channel_weight_observer
    )
    
    # 应用动态量化
    quantized_model = quantization.quantize_dynamic(
        model,
        QUANTIZATION_CONFIG['modules_to_quantize'],
        dtype=QUANTIZATION_CONFIG['dtype']
    )
    
    print("✅ 动态量化完成")
    return quantized_model

def save_quantized_model(model, save_path):
    """保存量化模型"""
    # 确保目录存在
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # 保存量化模型状态
    torch.save(model.state_dict(), save_path)
    
    # 记录模型信息
    file_size = os.path.getsize(save_path) / (1024 * 1024)  # MB
    print(f"💾 量化模型已保存: {save_path}")
    print(f"📦 文件大小: {file_size:.2f} MB")
    
    return save_path

# =============================
# 4. 量化验证函数
# =============================
def verify_quantization(original_model, quantized_model, test_input=None):
    """验证量化效果"""
    print("🧪 开始量化验证...")
    
    if test_input is None:
        # 创建测试输入
        test_input = torch.randn(1, 3, 224, 224)
    
    # 原始模型推理
    with torch.no_grad():
        original_model.eval()
        start_time = time.time()
        original_output = original_model(test_input)
        original_time = time.time() - start_time
        
        # 量化模型推理
        quantized_model.eval()
        start_time = time.time()
        quantized_output = quantized_model(test_input)
        quantized_time = time.time() - start_time
    
    # 计算加速比和精度差异
    speedup_ratio = original_time / quantized_time
    output_diff = torch.mean(torch.abs(original_output - quantized_output)).item()
    
    print(f"📊 量化验证结果:")
    print(f"   • 原始模型推理时间: {original_time*1000:.2f}ms")
    print(f"   • 量化模型推理时间: {quantized_time*1000:.2f}ms")
    print(f"   • 加速比例: {speedup_ratio:.2f}x")
    print(f"   • 输出差异: {output_diff:.6f}")
    
    return speedup_ratio, output_diff

# =============================
# 5. 完整量化流程
# =============================
def complete_quantization_pipeline():
    """完整的量化流程"""
    print("=" * 60)
    print("          河南AI模型量化流程启动")
    print("=" * 60)
    print(f"⏰ 开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 步骤1: 加载训练模型
        trained_model_path = MODEL_DIR / "trained.pth"
        original_model = load_trained_model(trained_model_path)
        
        # 步骤2: 应用量化
        quantized_model = apply_dynamic_quantization(original_model)
        
        # 步骤3: 保存量化模型
        quantized_model_path = MODEL_DIR / "quantized_model.pth"
        save_quantized_model(quantized_model, quantized_model_path)
        
        # 步骤4: 验证量化效果
        test_input = torch.randn(1, 3, 224, 224)  # 测试输入
        speedup_ratio, output_diff = verify_quantization(original_model, quantized_model, test_input)
        
        # 步骤5: 生成量化报告
        generate_quantization_report(original_model, quantized_model, speedup_ratio, output_diff)
        
        print("🎉 量化流程完成！")
        return True
        
    except Exception as e:
        print(f"❌ 量化过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_quantization_report(original_model, quantized_model, speedup_ratio, output_diff):
    """生成量化报告"""
    report = {
        'quantization_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'original_model_size': sum(p.numel() for p in original_model.parameters()),
        'quantized_model_size': sum(p.numel() for p in quantized_model.parameters()),
        'speedup_ratio': speedup_ratio,
        'output_difference': output_diff,
        'quantization_config': QUANTIZATION_CONFIG
    }
    
    # 保存报告
    report_path = MODEL_DIR / "quantization_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("河南AI模型量化报告\n")
        f.write("=" * 40 + "\n")
        for key, value in report.items():
            if key == 'quantization_config':
                f.write(f"{key}:\n")
                for k, v in value.items():
                    f.write(f"  {k}: {v}\n")
            else:
                f.write(f"{key}: {value}\n")
    
    print(f"📝 量化报告已保存: {report_path}")

# =============================
# 6. 主程序入口
# =============================
if __name__ == "__main__":
    # 设置随机种子确保可重复性
    torch.manual_seed(42)
    
    # 运行完整量化流程
    success = complete_quantization_pipeline()
    
    if success:
        print("\n✅ 量化成功完成！")
        print("💡 您现在可以:")
        print("   1. 在主程序中使用量化模型进行推理")
        print("   2. 查看量化报告了解性能提升")
        print("   3. 验证模型兼容性")
    else:
        print("\n❌ 量化流程失败")
        print("💡 建议检查:")
        print("   • trained.pth文件是否存在")
        print("   • 模型架构是否一致")
        print("   • PyTorch版本兼容性")
    
    print(f"\n⏰ 完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")