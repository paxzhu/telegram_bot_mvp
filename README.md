# Telegram Bot MVP

一个简单的 Telegram 机器人，提供 Instagram 动态查询和记忆生成图片功能。

## 功能特点

- 📸 Instagram 动态查询：查看指定用户的最近动态
- 🖼 图片生成：根据文本描述生成相关图片（目前使用示例图片）

## 环境要求

- Python 3.10+
- Telegram Bot Token

## 快速开始

1. 克隆仓库
```bash
git clone <repository-url>
cd telegram_bot_mvp
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 Telegram Bot Token
```

5. 运行机器人
```bash
python run.py
```

## 使用说明

1. 在 Telegram 中搜索你的机器人并开始对话
2. 使用以下命令：
   - `/start` - 显示主菜单
   - 选择 "📸 查看近况" 并输入 Instagram 用户名（例如：@username）
   - 选择 "🖼 讲述我的回忆" 并输入描述文本

## 项目结构

```
telegram_bot_mvp/
│
├─ bot/                       
│   ├─ __init__.py
│   ├─ handlers.py            # /start、按钮、文本统一入口
│   ├─ instagram.py           # 功能一：Instagram近况摘要
│   ├─ memory.py              # 功能二：记忆转图像
│   ├─ assets/                
│   │    └─ samples/          # 放 2-3 张 PNG 作占位
│   └─ data/
│       └─ fake_posts.json
│
├─ run.py                     # 启动脚本
├─ requirements.txt           # 项目依赖
├─ .env                       # 环境变量
├─ .env.example               # 环境变量示例
└─ README.md
```

## 开发说明

- 目前使用本地假数据模拟 Instagram 动态
- 图片生成功能使用示例图片，后续可集成 Stable Diffusion
- 所有代码都有详细的中文注释

## 许可证

MIT License

```bash
git clone https://github.com/yourname/telegram_bot_mvp.git
cd telegram_bot_mvp
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # 写入 BOT_TOKEN
python run.py                 # 本地长轮询
