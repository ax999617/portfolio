import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from PIL import Image, ImageTk, ImageEnhance
import torch
from torchvision import transforms
import os
import sys
import threading
import time
import json
from datetime import datetime
from functools import partial
import traceback

# ==============================
# 项目配置
# ==============================
try:
    SCRIPT_DIR = os.path.abspath(os.getcwd())
    PROJECT_ROOT = SCRIPT_DIR
    sys.path.insert(0, PROJECT_ROOT)
except Exception as e:
    print(f"[警告] 初始化路径失败: {e}")
    PROJECT_ROOT = os.getcwd()

# 知识库配置
KNOWLEDGE_PATH = os.path.join(PROJECT_ROOT, 'knowledge.json')

# 模型配置
MODEL_CONFIGS = {
    'quantized': {
        'module_path': 'quantized',
        'model_class': 'QuantizedHenanModel',
        'weight_file': os.path.join(PROJECT_ROOT, 'model', 'quantized_model.pth'),
        'description': '量化模型（低资源消耗）'
    },
    'trained': {
        'module_path': 'trained',
        'model_class': 'UltimateHenanCNN',
        'weight_file': os.path.join(PROJECT_ROOT, 'model', 'trained.pth'),
        'description': '完整训练模型（高精度）'
    }
}

# 默认配置（已修改为新类别）
DEFAULT_CONFIG = {
    'image_size': 224,
    'mean': [0.485, 0.456, 0.406],
    'std': [0.229, 0.224, 0.225],
    'num_classes': 3,
    'class_names': ["洛阳牡丹", "信阳毛尖茶树", "郑州商代青铜器"],
    'reference_images': {
        "洛阳牡丹": os.path.join(PROJECT_ROOT, 'reference_images', 'luoyang_peony_ref.jpg'),
        "信阳毛尖茶树": os.path.join(PROJECT_ROOT, 'reference_images', 'xinyang_maojian_ref.jpg'),
        "郑州商代青铜器": os.path.join(PROJECT_ROOT, 'reference_images', 'zhengzhou_bronze_ref.jpg')
    }
}

# ==============================
# 核心功能模块
# ==============================
class ModelManager:
    def __init__(self):
        self.models = {}
        self.current_model = None
        self.load_config()

    def load_config(self):
        try:
            config_path = os.path.join(PROJECT_ROOT, 'model_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.model_config = json.load(f)
            else:
                self.model_config = MODEL_CONFIGS
        except Exception as e:
            print(f"[ModelError] 加载模型配置失败: {str(e)}")
            self.model_config = MODEL_CONFIGS

    def get_model(self, model_type='trained'):
        if model_type in self.models:
            return self.models[model_type]
            
        try:
            config = self.model_config.get(model_type)
            if not config:
                raise ValueError(f"未知模型类型: {model_type}")
                
            module = __import__(config['module_path'], fromlist=[config['model_class']])
            model_class = getattr(module, config['model_class'])
            model = model_class(num_classes=DEFAULT_CONFIG['num_classes'])
            
            weight_path = os.path.join(PROJECT_ROOT, config['weight_file'])
            if os.path.exists(weight_path):
                state = torch.load(weight_path, map_location='cpu')
                if isinstance(state, dict) and 'state_dict' in state:
                    state = state['state_dict']
                model.load_state_dict(state, strict=False)
                
            model.eval()
            self.models[model_type] = model
            return model
            
        except Exception as e:
            print(f"[ModelError] {str(e)}")
            return self.create_fallback_model()

    def create_fallback_model(self):
        return torch.nn.Sequential(
            torch.nn.Conv2d(3, 32, 3, padding=1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),
            torch.nn.Conv2d(32, 64, 3, padding=1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),
            torch.nn.AdaptiveAvgPool2d((1, 1)),
            torch.nn.Flatten(),
            torch.nn.Linear(64, DEFAULT_CONFIG['num_classes'])
        )

class ImageProcessor:
    def __init__(self):
        self.transforms = transforms.Compose([
            transforms.Resize((DEFAULT_CONFIG['image_size'], DEFAULT_CONFIG['image_size'])),
            transforms.ToTensor(),
            transforms.Normalize(mean=DEFAULT_CONFIG['mean'], std=DEFAULT_CONFIG['std']),
        ])

    def preprocess(self, image_path):
        try:
            image = Image.open(image_path).convert('RGB')
            return self.transforms(image).unsqueeze(0)
        except Exception as e:
            print(f"[ImageError] {str(e)}")
            raise

class HistoryManager:
    def __init__(self):
        self.history_file = os.path.join(PROJECT_ROOT, 'history.json')
        self.load_history()

    def load_history(self):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            else:
                self.history = []
        except Exception as e:
            print(f"[HistoryError] 加载历史记录失败: {str(e)}")
            self.history = []

    def save_history(self):
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"[HistoryError] 保存历史记录失败: {str(e)}")

    def add_entry(self, entry):
        self.history.insert(0, entry)
        if len(self.history) > 20:
            self.history.pop()
        self.save_history()

class KnowledgeManager:
    def __init__(self):
        self.knowledge_file = KNOWLEDGE_PATH
        self.load_knowledge()

    def load_knowledge(self):
        try:
            if os.path.exists(self.knowledge_file):
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    self.knowledge = json.load(f)
            else:
                self.knowledge = {}
        except Exception as e:
            print(f"[KnowledgeError] 加载知识库失败: {str(e)}")
            self.knowledge = {}

    def get_knowledge(self, class_name):
        return self.knowledge.get(class_name, {
            "title": "暂无知识",
            "description": "尚未添加该类别的科普知识",
            "features": []
        })
# ==============================
# 主应用类
# ==============================
class AIRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.model_manager = ModelManager()
        self.image_processor = ImageProcessor()
        self.history_manager = HistoryManager()
        self.knowledge_manager = KnowledgeManager()
        
        self.init_styles()
        
        # 设置窗口标题
        self.root.title("智能物体识别系统")
        
        self.create_widgets()
        self.load_current_model()
        self.center_window()
        self.setup_bindings()
        
    def init_styles(self):
        """初始化样式"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 自定义样式
        self.style.configure('Title.TLabel', 
                            font=('Microsoft YaHei UI', 16, 'bold'),
                            background='#2E2E2E',
                            foreground='white')
                            
        self.style.configure('Header.TFrame',
                            background='#2E2E2E')
                            
        self.style.configure('Button.TButton',
                            padding=6,
                            relief='flat',
                            background='#4472C4',
                            foreground='white')
        self.style.map('Button.TButton',
                      background=[('active', '#3B5998')])
                      
        self.style.configure('Model.TCombobox',
                            fieldbackground='#1E1E1E',
                            background='#1E1E1E',
                            foreground='white',
                            insertcolor='white')
                            
        self.style.configure('Image.TFrame',
                            background='#3C3F41')
                            
        self.style.configure('Result.TLabel',
                            font=('Microsoft YaHei UI', 12, 'bold'),
                            foreground='green')
                            
        self.style.configure('Status.TLabel',
                            font=('Consolas', 9),
                            foreground='#CCCCCC',
                            background='#222222')
        self.style.configure('Knowledge.TButton', 
                            background='#2E2E2E', 
                            foreground='white')

    def create_widgets(self):
        """创建所有界面组件"""
        # 窗口配置
        self.root.geometry("1280x800")
        self.root.configure(bg='#1E1E1E')
        
        # 创建主容器
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标题栏
        header = ttk.Frame(main_container, style='Header.TFrame')
        header.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header, text="智能物体识别系统", style='Title.TLabel')
        title_label.pack(pady=5)
        
        # 工具栏
        toolbar = ttk.Frame(main_container)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        self.model_var = tk.StringVar(value='trained')
        self.model_combo = ttk.Combobox(toolbar, textvariable=self.model_var, 
                                      values=list(MODEL_CONFIGS.keys()), 
                                      style='Model.TCombobox', width=15)
        self.model_combo.pack(side=tk.LEFT, padx=5)
        self.model_combo.bind('<<ComboboxSelected>>', self.change_model)
        
        refresh_btn = ttk.Button(toolbar, text="🔄 刷新模型", 
                               command=self.refresh_model, 
                               style='Button.TButton')
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        config_btn = ttk.Button(toolbar, text="⚙️ 配置", 
                              command=self.show_config, 
                              style='Button.TButton')
        config_btn.pack(side=tk.LEFT, padx=5)
        
        history_btn = ttk.Button(toolbar, text="🕒 历史记录", 
                               command=self.show_history, 
                               style='Button.TButton')
        history_btn.pack(side=tk.LEFT, padx=5)
        
        # 主工作区
        work_area = ttk.Frame(main_container)
        work_area.pack(fill=tk.BOTH, expand=True)
        
        # 左侧图片区域
        image_frame = ttk.Frame(work_area, style='Image.TFrame')
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # 使用 tk.Label 替代 ttk.Label 并设置像素大小
        self.image_label = tk.Label(
            image_frame,
            text="请上传图片",
            anchor=tk.CENTER,
            bg="#3C3F41",  # 保持与原样式一致
            fg="white",
            relief=tk.SUNKEN,
            bd=2
        )
        self.image_label.place(relx=0.5, rely=0.5, width=400, height=400, anchor=tk.CENTER)
        
        # 右侧控制面板
        control_frame = ttk.Frame(work_area)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        # 上传按钮
        upload_btn = ttk.Button(control_frame, text="📂 上传图片", 
                              command=self.upload_image,
                              style='Button.TButton')
        upload_btn.pack(pady=10, fill=tk.X)
        
        # 拖放提示
        drop_label = ttk.Label(control_frame, text="或拖拽图片至此区域",
                             foreground='gray',
                             justify=tk.CENTER)
        drop_label.pack(pady=5)
        
        # 进度指示
        self.progress = ttk.Progressbar(control_frame, mode='indeterminate')
        self.progress.pack(pady=5, fill=tk.X)
        
        # 识别结果
        result_frame = ttk.LabelFrame(control_frame, text="🔍 识别结果")
        result_frame.pack(fill=tk.X, pady=10)
        
        self.result_label = tk.Label(  # 替换为 tk.Label
            result_frame,
            text="等待识别...",
            font=('Microsoft YaHei UI', 12, 'bold'),
            foreground='green',
            bg="#3C3F41"  # 与父容器背景色一致
        )
        self.result_label.pack(padx=10, pady=10)
        
        # 参考图片区域
        reference_frame = ttk.LabelFrame(control_frame, text="🎯 相关物品参考")
        reference_frame.pack(fill=tk.X, pady=10)
        
        self.ref_labels = []
        for i in range(2):
            ref_label = tk.Label(reference_frame, text=f"参考{i+1}", bg="#3C3F41", fg="white", bd=2, relief=tk.SUNKEN)
            ref_label.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
            self.ref_labels.append(ref_label)
            ref_label.bind("<Button-1>", lambda e, idx=i: self.show_knowledge(DEFAULT_CONFIG['class_names'][idx]))
        
        # 状态栏
        status_frame = ttk.Frame(self.root, style='Status.TFrame')
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="就绪", 
                                    style='Status.TLabel')
        self.status_label.pack(padx=10)
        
    def center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_bindings(self):
        """设置事件绑定"""
        self.root.bind('<Button-1>', self.on_mouse_click)
        
    def on_mouse_click(self, event):
        """鼠标点击事件"""
        widget = event.widget
        if isinstance(widget, tk.Label) and widget == self.image_label:
            self.upload_image()
            
    def load_current_model(self):
        """加载当前模型"""
        try:
            self.model = self.model_manager.get_model(self.model_var.get())
            self.status_label.config(text=f"模型 {self.model_var.get()} 加载成功")
        except Exception as e:
            self.status_label.config(text=f"模型加载失败: {str(e)}")
            messagebox.showerror("模型错误", str(e))
            
    def change_model(self, event=None):
        """切换模型"""
        model_type = self.model_var.get()
        self.progress.start()
        self.status_label.config(text=f"正在加载模型: {model_type}")
        
        def _load():
            try:
                self.model = self.model_manager.get_model(model_type)
                self.status_label.config(text=f"模型 {model_type} 加载完成")
            except Exception as e:
                self.status_label.config(text=f"模型加载失败: {str(e)}")
                messagebox.showerror("模型错误", str(e))
            finally:
                self.progress.stop()
                
        threading.Thread(target=_load).start()
            
    def refresh_model(self):
        """刷新模型"""
        self.model_manager.load_config()
        self.model_combo['values'] = list(self.model_manager.model_config.keys())
        self.change_model()
        
    def upload_image(self):
        """上传图片"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if file_path:
            self.process_file(file_path)
            
    def process_file(self, file_path):
        """处理文件"""
        self.progress.start()
        self.status_label.config(text="正在处理图片...")
        self.result_label.config(text="识别中...", foreground='green')
        
        def _process():
            try:
                # 显示图片
                self.show_image(file_path)
                
                # 预处理
                input_tensor = self.image_processor.preprocess(file_path)
                
                # 设备分配
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                input_tensor = input_tensor.to(device)
                self.model.to(device)
                
                # 执行预测
                with torch.no_grad():
                    output = self.model(input_tensor)
                    top2 = torch.topk(output, 2)
                    _, predicted = top2
                    
                class_ids = predicted.cpu().numpy()[0]
                class_names = [DEFAULT_CONFIG['class_names'][id] for id in class_ids]
                
                # 显示结果
                self.root.after(0, self.show_result, class_names)
                self.root.after(0, self.show_reference_images, class_names)
                
                # 记录历史
                entry = {
                    'timestamp': datetime.now().isoformat(),
                    'file': file_path,
                    'model': self.model_var.get(),
                    'result': class_names
                }
                self.history_manager.add_entry(entry)
                
                self.status_label.config(text="识别完成")
                
            except Exception as e:
                error_msg = f"处理失败: {str(e)}"
                self.root.after(0, self.show_error, error_msg)
                self.status_label.config(text=error_msg)
            finally:
                self.root.after(0, self.progress.stop)
                
        threading.Thread(target=_process).start()
            
    def show_image(self, file_path):
        """显示图片"""
        try:
            image = Image.open(file_path)
            max_size = (400, 400)
            image.thumbnail(max_size)
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo
        except Exception as e:
            self.show_error(f"图片显示失败: {str(e)}")
            
    def show_result(self, result_text):
        """显示识别结果"""
        self.result_label.config(text=f"识别结果: {', '.join(result_text)}", foreground='green')
            
    def show_error(self, error_text):
        """显示错误信息"""
        self.result_label.config(text=error_text, foreground='red')
    
    def show_reference_images(self, class_names):
        """显示参考图片"""
        try:
            for i, label in enumerate(self.ref_labels):
                # 确保class_name在知识库中存在（容错处理）
                class_name = class_names[i] if (i < len(class_names) and class_names[i] in self.knowledge_manager.knowledge) else None
                if not class_name:
                    label.config(text=f"参考{i+1}", image="", fg="white")
                    continue
                    
                ref_path = DEFAULT_CONFIG['reference_images'].get(class_name, "")
                
                if ref_path and os.path.exists(ref_path):
                    ref_img = Image.open(ref_path)
                    ref_img.thumbnail((150, 150))
                    ref_photo = ImageTk.PhotoImage(ref_img)
                    label.config(image=ref_photo, text="")
                    label.image = ref_photo
                    # 绑定点击事件，传递正确的class_name（与知识库key一致）
                    label.unbind("<Button-1>")
                    label.bind("<Button-1>", lambda e, cn=class_name: self.show_knowledge(cn))
                else:
                    label.config(text=f"参考{i+1}", image="", fg="white")
                    
        except Exception as e:
            print(f"[Error] 显示参考图片失败: {str(e)}")
            
    def show_knowledge(self, class_name):
        """显示科普知识"""
        knowledge = self.knowledge_manager.get_knowledge(class_name)
        
        # 创建知识弹窗
        knowledge_window = tk.Toplevel(self.root)
        knowledge_window.title(f"{class_name} 科普知识")
        knowledge_window.geometry("400x400")
        knowledge_window.transient(self.root)
        knowledge_window.configure(bg='#2E2E2E')
        
        # 添加关闭按钮
        close_btn = ttk.Button(knowledge_window, text="×", command=knowledge_window.destroy, style='Button.TButton')
        close_btn.pack(anchor='ne', padx=5, pady=5)
        
        # 标题
        title_label = ttk.Label(knowledge_window, text=knowledge.get("title", class_name), 
                              font=('Microsoft YaHei UI', 14, 'bold'), background='#2E2E2E', foreground='white')
        title_label.pack(pady=10)
        
        # 描述
        desc_label = ttk.Label(knowledge_window, text=knowledge.get("description", "暂无描述"),
                             wraplength=380, justify=tk.LEFT, background='#2E2E2E', foreground='white')
        desc_label.pack(pady=10)
        
        # 特征列表
        if "features" in knowledge and knowledge["features"]:
            features_frame = ttk.Frame(knowledge_window)
            features_frame.pack(pady=10)
            
            for feature in knowledge["features"]:
                feature_label = ttk.Label(features_frame, text=f"• {feature}", 
                                        font=('Microsoft YaHei UI', 10), background='#2E2E2E', foreground='white')
                feature_label.pack(anchor='w', pady=2)
        
        # 图片展示（优化：添加文件夹创建逻辑，避免路径不存在错误）
        if "image" in knowledge and knowledge["image"]:
            try:
                img_path = os.path.join(PROJECT_ROOT, knowledge["image"])
                # 新增：创建knowledge_images文件夹（如果不存在）
                img_dir = os.path.dirname(img_path)
                if not os.path.exists(img_dir):
                    os.makedirs(img_dir)
                # 图片存在则显示，不存在不报错
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    img.thumbnail((300, 300))
                    photo = ImageTk.PhotoImage(img)
                    img_label = ttk.Label(knowledge_window, image=photo, background='#2E2E2E')
                    img_label.image = photo
                    img_label.pack(pady=10)
            except Exception as e:
                print(f"[Error] 加载知识图片失败: {str(e)}")
            
    def show_config(self):
        """显示配置对话框"""
        config_window = tk.Toplevel(self.root)
        config_window.title("系统配置")
        config_window.geometry("400x300")
        config_window.transient(self.root)
        config_window.configure(bg='#2E2E2E')
        
        # 类别配置
        class_frame = ttk.LabelFrame(config_window, text="类别配置", style='Header.TFrame')
        class_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.class_entries = []
        for i, name in enumerate(DEFAULT_CONFIG['class_names']):
            entry = ttk.Entry(class_frame)
            entry.insert(0, name)
            entry.pack(pady=2, fill=tk.X)
            self.class_entries.append(entry)
            
        # 图像配置
        image_frame = ttk.LabelFrame(config_window, text="图像处理配置", style='Header.TFrame')
        image_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.size_var = tk.StringVar(value=str(DEFAULT_CONFIG['image_size']))
        size_entry = ttk.Entry(image_frame, textvariable=self.size_var, width=10)
        size_entry.pack(pady=2)
        
        # 保存按钮
        save_btn = ttk.Button(config_window, text="保存配置", 
                            command=self.save_config, 
                            style='Button.TButton')
        save_btn.pack(pady=10)
        
    def save_config(self):
        """保存配置"""
        try:
            new_classes = [e.get() for e in self.class_entries]
            new_size = int(self.size_var.get())
            
            if len(new_classes) != len(DEFAULT_CONFIG['class_names']):
                raise ValueError("类别数量不匹配")
                
            if new_size <= 0:
                raise ValueError("尺寸必须大于0")
                
            DEFAULT_CONFIG['class_names'] = new_classes
            DEFAULT_CONFIG['image_size'] = new_size
            
            messagebox.showinfo("成功", "配置已保存")
            self.show_result("等待识别...")
        except Exception as e:
            messagebox.showerror("配置错误", str(e))
            
    def show_history(self):
        """显示历史记录"""
        history_window = tk.Toplevel(self.root)
        history_window.title("识别历史")
        history_window.geometry("600x400")
        history_window.transient(self.root)
        history_window.configure(bg='#2E2E2E')
        
        tree = ttk.Treeview(history_window, columns=("时间", "模型", "结果"), 
                          show="headings")
        tree.heading("时间", text="时间")
        tree.heading("模型", text="模型")
        tree.heading("结果", text="结果")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for entry in self.history_manager.history:
            result_str = ", ".join(entry['result']) if isinstance(entry['result'], list) else entry['result']
            tree.insert("", "end", values=(
                entry['timestamp'][:19],
                entry['model'],
                result_str
            ))
            
        # 添加导出按钮
        export_btn = ttk.Button(history_window, text="导出为CSV", 
                              command=lambda: self.export_history(tree),
                              style='Button.TButton')
        export_btn.pack(pady=10)
        
    def export_history(self, tree):
        """导出历史记录"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV 文件", "*.csv")]
            )
            if not file_path:
                return
                
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("时间,模型,结果\n")
                for item in tree.get_children():
                    values = tree.item(item)['values']
                    f.write(f"{','.join(values)}\n")
                    
            messagebox.showinfo("成功", "历史记录已导出")
        except Exception as e:
            messagebox.showerror("导出错误", str(e))

# ==============================
# 启动应用
# ==============================
if __name__ == "__main__":
    # 创建默认配置文件
    model_config_path = os.path.join(PROJECT_ROOT, 'model_config.json')
    if not os.path.exists(model_config_path):
        with open(model_config_path, 'w') as f:
            json.dump(MODEL_CONFIGS, f, indent=2)
    
    # 创建知识库文件（重点修改：替换为新类别默认知识）
    if not os.path.exists(KNOWLEDGE_PATH):
        default_knowledge = {
            "洛阳牡丹": {
                "title": "洛阳牡丹",
                "description": "洛阳牡丹是中国著名的观赏花卉，有“花中之王”的美誉。洛阳种植牡丹历史悠久，品种繁多，花色丰富，以雍容华贵、富丽堂皇著称。每年四月的洛阳牡丹花会吸引海内外游客前来观赏。",
                "features": [
                    "历史悠久，种植可追溯至唐代",
                    "品种繁多，有红、白、粉、紫等多种颜色",
                    "花型多样，包括单瓣、重瓣、千瓣等",
                    "具有较高的观赏价值和文化象征意义"
                ],
                "image": "knowledge_images/luoyang_peony.jpg"
            },
            "信阳毛尖茶树": {
                "title": "信阳毛尖茶树",
                "description": "信阳毛尖茶树主要种植于河南省信阳市，是中国十大名茶之一“信阳毛尖”的原料来源。茶树生长在高海拔、多云雾的山区，叶片细嫩，富含茶多酚和氨基酸，造就了信阳毛尖独特的香气和口感。",
                "features": [
                    "生长于高海拔、多云雾的山区",
                    "叶片细嫩，富含茶多酚和氨基酸",
                    "采摘时间严格，以春季嫩芽为主",
                    "成品茶叶条索紧细、色泽翠绿、香气清高"
                ],
                "image": "knowledge_images/xinyang_maojian.jpg"
            },
            "郑州商代青铜器": {
                "title": "郑州商代青铜器",
                "description": "郑州是商代早期的重要都城之一，出土了大量商代青铜器，包括鼎、觚、爵、斝等。这些青铜器工艺精湛，造型庄重，纹饰精美，反映了商代高超的铸造技术和礼制文化。",
                "features": [
                    "铸造工艺精湛，采用范铸法",
                    "器型多样，包括礼器、兵器、工具等",
                    "纹饰精美，常见兽面纹、云雷纹等",
                    "具有重要的历史、文化和艺术价值"
                ],
                "image": "knowledge_images/zhengzhou_bronze.jpg"
            }
        }
        with open(KNOWLEDGE_PATH, 'w', encoding='utf-8') as f:
            json.dump(default_knowledge, f, indent=2)
    
    root = tk.Tk()
    app = AIRecognitionApp(root)
    root.mainloop()