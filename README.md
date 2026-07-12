# Agent

一个基于 DeepSeek API 和 PySide6 构建的智能体模块，用于个人使用。

目标是想做个有鲜明性格，有自己生活，但又能帮我完成部分工作的智能体。  
那时它会兼具一些角色扮演与AI编程应用的功能呢。

不过目前还只是一个简陋的版本啦，才刚刚实现对话功能。

该模块可作为独立应用启动，也可嵌入到主程序（资料库：`assistant`）中。

## 启动方式

### 第一步：安装依赖

```bash
pip install -r requirements.txt
```

### 第二步：配置环境变量

需要设置 DeepSeek API 密钥：

```bash
export DEEPSEEK_API_KEY="your-api-key"
```

如果想要其他模型暂时还只能手动配置。

### 第三步：运行应用程序

#### 方式一：从主程序启动

从`assistant`的主界面“应用”一栏启动。

#### 方式二：直接启动单独窗口

从该目录内运行：

```bash
python run.py
```

## 项目构建过程的参考资料库

- TheSyart / claude-agent-examples
- HKUDS/nanobot
