from typing import Dict

# 三语文案表；Key → zh, ja, en
_TRANSLATIONS: Dict[str, tuple[str, str, str]] = {
    "welcome": (
        "您好！请选择功能：",
        "こんにちは！メニューを選択してください：",
        "Hi! Please choose an option:"
    ),
    "cancel_ok": (
        "已取消当前操作。",
        "操作をキャンセルしました。",
        "Cancelled."
    ),
    "ask_instagram": (
        "请输入 Instagram 用户名或带 @ 的句子：",
        "Instagram のユーザー名（@含む）を入力してください：",
        "Please enter an Instagram handle (@username):"
    ),
    "ask_memory": (
        "请描述一段回忆，我会为你生成写实图像：",
        "思い出を教えてください。リアルな画像を生成します：",
        "Describe a memory and I'll generate an image:"
    ),
    "no_caption": (
        "⚠️ 未识别用户名，请重新输入，例如：@natgeo",
        "⚠️ ユーザー名を認識できません。例：@natgeo",
        "⚠️ Could not recognise handle, eg: @natgeo"
    ),
    "private_or_none": (
        "❌ 账号不存在或为私密账号。",
        "❌ アカウントが存在しないか非公開です。",
        "❌ Account not found or private."
    ),
    "no_posts": (
        "⚠️ 没抓到贴文，也许账号为空或受限。",
        "⚠️ 投稿が取得できませんでした。",
        "⚠️ No posts found."
    ),
    "your_memory_img": (
        "✨ 你的回忆图像已生成",
        "✨ 思い出の画像を生成しました",
        "✨ Generated your memory image"
    ),
    "empty_memory_description": (
        "⚠️ 描述不能为空，请重新输入。",
        "⚠️ 説明は空にできません。再度入力してください。",
        "⚠️ Description cannot be empty. Please try again."
    ),
    "image_generation_failed": (
        "❌ 图像生成失败，请稍后重试。",
        "❌ 画像生成に失敗しました。しばらくしてから再試行してください。",
        "❌ Image generation failed. Please try again later."
    ),
}

def tr(key: str, lang_code: str | None) -> str:
    """返回 key 对应的文本, 根据 Telegram lang_code 选择 zh / ja / en."""
    zh, ja, en = _TRANSLATIONS[key]
    if not lang_code:
        return en
    l = lang_code.lower()
    if l.startswith("ja"):
        return ja
    if l.startswith("zh"):
        return zh
    return en  # default 简体中文

__all__ = ["tr"]