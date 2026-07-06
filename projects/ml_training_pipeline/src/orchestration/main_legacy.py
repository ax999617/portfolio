import torch
import torch.nn as nn
import os
import sys
import time
import traceback
import subprocess  # ✅ 新增模块
from datetime import datetime

# =============================
# 修复1：定义脚本绝对路径
# =============================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = SCRIPT_DIR
sys.path.insert(0, PROJECT_ROOT)  # 优先使用项目根目录

print(f"📁 项目根目录: {PROJECT_ROOT}")
print(f"📁 当前工作目录: {os.getcwd()}")

# =============================
# 修复2：使用绝对路径配置模型文件（修正训练文件名为trained.pth）
# =============================
MODEL_CONFIGS = {
    'quantized': {
        'module_path': 'quantized',
        'model_class': 'QuantizedHenanModel',
        'weight_file': os.path.join(PROJECT_ROOT, 'model', 'quantized_model.pth')
    },
    'trained': {
        'module_path': 'trained',
        'model_class': 'UltimateHenanCNN',
        'weight_file': os.path.join(PROJECT_ROOT, 'model', 'trained.pth')  # 修正为trained.pth
    }
}

def robust_path_resolver(relative_path):
    """健壮的路径解析器"""
    possible_paths = [
        os.path.join(PROJECT_ROOT, relative_path),  # 基于项目根目录
        os.path.join(os.getcwd(), relative_path),   # 基于当前工作目录
        relative_path                               # 原始路径
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return os.path.abspath(path)
    
    return os.path.join(PROJECT_ROOT, relative_path)

def universal_model_loader(model_type='quantized', num_classes=3):
    """万能模型加载器（支持 quantized / trained）"""
    print(f"🔧 启动模型加载系统... 类型: {model_type.upper()}")

    config = MODEL_CONFIGS.get(model_type)
    if not config:
        raise ValueError(f"不支持的模型类型: {model_type}")

    module_name = config['module_path']
    class_name = config['model_class']
    weight_path = robust_path_resolver(config['weight_file'])
    
    print(f"📊 路径分析详情:")
    print(f"   • 配置路径: {config['weight_file']}")
    print(f"   • 解析后路径: {weight_path}")
    print(f"   • 文件存在: {os.path.exists(weight_path)}")

    try:
        try:
            module = __import__(module_name, fromlist=[class_name])
            ModelClass = getattr(module, class_name)
        except ImportError as e:
            print(f"❌ 模块导入失败: {e}")
            return create_emergency_fallback(num_classes)

        model = ModelClass(num_classes=num_classes)
        print(f"✅ {class_name} 实例化成功")

        if not os.path.exists(weight_path):
            print(f"⚠️ 权重文件不存在: {weight_path}")
            print("💡 使用随机初始化模型")
            return model

        saved_state = torch.load(weight_path, map_location='cpu')

        if isinstance(saved_state, dict) and 'state_dict' in saved_state:
            saved_state = saved_state['state_dict']

        model.load_state_dict(saved_state, strict=False)
        print("✅ 模型权重加载完成（非严格模式）")

        model_keys = set(model.state_dict().keys())
        saved_keys = set(saved_state.keys())
        matched = model_keys & saved_keys
        missing = model_keys - saved_keys
        unexpected = saved_keys - model_keys

        print(f"📊 加载分析:")
        print(f"   • 应有层数: {len(model_keys)}")
        print(f"   • 提供层数: {len(saved_keys)}")
        print(f"   • 成功匹配: {len(matched)}")
        if missing:
            print(f"   • 缺失层: {list(missing)[:3]}{'...' if len(missing)>3 else ''}")
        if unexpected:
            print(f"   • 多余层: {list(unexpected)[:3]}{'...' if len(unexpected)>3 else ''}")

        return model

    except Exception as e:
        print(f"❌ 模型加载失败 ({model_type}): {e}")
        return create_emergency_fallback(num_classes)

def create_emergency_fallback(num_classes=3):
    """紧急回退模型（100%可用性保证）"""
    print("🚨 启动紧急回退方案...")

    model = nn.Sequential(
        nn.Conv2d(3, 32, 3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(32, 64, 3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.AdaptiveAvgPool2d((1, 1)),
        nn.Flatten(),
        nn.Linear(64, num_classes)
    )

    print("✅ 紧急回退模型创建完成")
    return model

def comprehensive_system_diagnostic():
    """综合系统诊断"""
    print("=" * 60)
    print("          通用AI科普系统诊断")
    print("=" * 60)

    checks = []

    try:
        torch_version = torch.__version__
        cuda_available = torch.cuda.is_available()
        checks.append(("PyTorch环境", f"✅ 版本{torch_version}, CUDA:{cuda_available}"))
    except Exception as e:
        checks.append(("PyTorch环境", f"❌ 异常: {str(e)}"))

    for name, cfg in MODEL_CONFIGS.items():
        try:
            __import__(cfg['module_path'])
            weight_ok = os.path.exists(robust_path_resolver(cfg['weight_file']))
            status = "✅ 存在" if weight_ok else "⚠️ 文件缺失"
            checks.append((f"{name}模型", status))
        except Exception as e:
            checks.append((f"{name}模型", f"❌ 导入失败: {e}"))

    for name, status in checks:
        print(f"• {name}: {status}")

    success_count = sum(1 for _, s in checks if "✅" in s)
    total_count = len(checks)
    success_rate = success_count / total_count * 100

    print(f"📊 系统健康度: {success_rate:.1f}% ({success_count}/{total_count})")
    return success_rate >= 50.0

def launch_ultimate_demo(model_type='quantized'):
    """启动演示系统（可选模型类型）"""
    print("\n" + "=" * 60)
    print(f"          通用AI科普系统启动 [{model_type}]")
    print("=" * 60)

    model = universal_model_loader(model_type=model_type, num_classes=3)

    print(f"🧠 当前加载模型: {MODEL_CONFIGS[model_type]['model_class']}")
    print(f"💾 权重路径: {robust_path_resolver(MODEL_CONFIGS[model_type]['weight_file'])}")

    print("💡 提示：可通过修改 launch_ultimate_demo('trained') 切换至高精度模型")
    print("🎉 通用AI科普系统启动完成！")
    return True

def main():
    """主函数（终极错误处理）"""
    print("🚀 通用AI科普系统启动中...")
    print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    model_dir = os.path.join(PROJECT_ROOT, 'model')
    if not os.path.exists(model_dir):
        os.makedirs(model_dir, exist_ok=True)
        print(f"📂 创建模型目录: {model_dir}")

    if not comprehensive_system_diagnostic():
        print("⚠️ 系统检查有警告，尝试继续运行...")

    MODEL_CHOICE = 'trained'  # 默认使用训练模型

    try:
        success = launch_ultimate_demo(model_type=MODEL_CHOICE)
        if success:
            print("✅ 系统启动成功")

            # =============================
            # ✅ 自动启动 GUI
            # =============================
            gui_path = os.path.join(PROJECT_ROOT, 'GUId.py')
            
            if os.path.exists(gui_path):
                print(f"🖥️ 正在启动 GUI: {gui_path}")
                # 使用当前Python解释器启动GUI，确保环境一致性
                subprocess.Popen([sys.executable, gui_path])
            else:
                print(f"❌ GUI 文件不存在: {gui_path}")
                print("💡 请确认GUId.py文件存在于项目根目录")

        else:
            print("❌ 系统启动失败")
    except Exception as e:
        print(f"💥 系统运行异常: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    torch.backends.cudnn.benchmark = True

    def global_exception_handler(exctype, value, tb):
        print("💥 全局异常捕获:")
        traceback.print_exception(exctype, value, tb)
        print("🛡️ 系统进入安全模式...")
        sys.exit(1)

    sys.excepthook = global_exception_handler
    main()