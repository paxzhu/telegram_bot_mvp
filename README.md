### 快速开始

```bash
git clone https://github.com/yourname/telegram_bot_mvp.git
cd telegram_bot_mvp
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # 写入 BOT_TOKEN
python run.py                 # 本地长轮询
