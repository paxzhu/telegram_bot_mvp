import json, pathlib, random

# 构建数据文件路径
data_file = pathlib.Path(__file__).parent / "data" / "fake_posts.json"
_FAKE_POSTS = json.loads(data_file.read_text(encoding="utf-8"))

def summarize(username: str) -> str | None:
    """
    读取本地假数据并拼接摘要。
    返回 None 表示用户不存在。
    """
    u = username.lstrip("@").lower()
    posts = _FAKE_POSTS.get(u)
    if not posts:
        return None

    selected = random.sample(posts, k=min(3, len(posts)))
    captions = "；".join(p["caption"] for p in selected)
    return f"@{u} 最近动态：{captions}"
