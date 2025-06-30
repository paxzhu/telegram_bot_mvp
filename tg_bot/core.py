from __future__ import annotations

import asyncio
import json
import os
import base64
import datetime as _dt
from typing import List, Dict, Union
import structlog
import requests
from pathlib import Path
from apify_client import ApifyClient
import google.generativeai as genai
import openai
from tg_bot.config import APIFY_TOKEN, GOOGLE_API_KEY, OPENAI_API_KEY
from tg_bot.exceptions import APIError

logger = structlog.get_logger("core")

# OpenAI client
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

# 输出图片保存目录 ----------------------------------------------------
IMAGE_DIR = Path(__file__).resolve().parent / "generated_images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)


# Apify & Gemini init -------------------------------------------------
_client = ApifyClient(APIFY_TOKEN)

GEN_TEXT_MODEL = "gemini-2.0-flash"
ENGINE = "stable-diffusion-xl-1024-v1-0"
genai.configure(api_key=GOOGLE_API_KEY)
_text_model = genai.GenerativeModel(GEN_TEXT_MODEL)

# ------------------------------------------------------------------
# Instagram 抓取
# ------------------------------------------------------------------
async def fetch_posts(username: str, limit: int = 3) -> List[str]:
    """返回给定用户最近 *limit* 条贴文 caption 列表。阻塞 SDK → 线程池。"""

    loop = asyncio.get_running_loop()

    def _scrape() -> List[str]:
        logger.info("Apify scrape ▶", username=username)
        actor = _client.actor("apify/instagram-scraper")
        run = actor.call(
            run_input={
                "directUrls": [f"https://www.instagram.com/{username}/"],
                "resultsType": "posts",
                "resultsLimit": limit,
                "savePostsSeparately": False,
            },
            timeout_secs=120,
        )
        dataset = _client.dataset(run["defaultDatasetId"])
        captions = [it["caption"] for it in dataset.iterate_items() if it.get("caption", "").strip()]
        logger.info("Apify scrape ✔", fetched=len(captions))
        return captions

    try:
        return await loop.run_in_executor(None, _scrape)
    except Exception as exc:
        logger.exception("Apify 抓取失败")
        raise APIError("抓取 Instagram 内容失败，请稍后重试。") from exc

# ------------------------------------------------------------------
# 摘要生成
# ------------------------------------------------------------------
async def summarize(captions: List[str], lang_code: str = 'English') -> str:
    if not captions:
        return "未获取到任何动态内容"

    prompt = (
        "You are an assistant skilled in analyzing social media content. "
        "Please summarize the recent statuses based on the following Instagram posts "
        f"and respond in one natural, concise English sentence. \n\n"
        "Instagram posts: \n" + "\n".join(f"- {c}" for c in captions)
    )
    logger.info("Prompt 生成", prompt=prompt)
    loop = asyncio.get_running_loop()
    try:
        rsp = await loop.run_in_executor(None, _text_model.generate_content, prompt)
    except Exception as exc:
        logger.exception("Gemini 调用失败")
        raise APIError("生成摘要失败，请稍后再试。") from exc

    return rsp.text.strip()

# ------------------------------------------------------------------
# 记忆 → 图像
# ------------------------------------------------------------------
# ---------------------------------------------------------------------
# LLM 系统提示词：Creative Director
# ---------------------------------------------------------------------
_CREATIVE_SYS_PROMPT = """
你是一位顶级的提示语工程师，你的唯一任务是为图像生成模型DALL-E 3创建超级写实 (Hyper-realistic) 的提示语。

你会收到一段由日本老年人以第一人称“我”叙述的、简短的日文个人回忆。请严格遵循我给出的范例，将其转换成一个旨在生成照片般逼真图像的英文提示语。最终图像必须看起来像真实拍摄的照片，采用第三人称观察者视角，能够完整地展现人物、情感和环境，而不仅仅是展示物体或动作。

**你的输出规则：**
1.  最终的回答**必须是一个纯粹的JSON对象**。
2.  **回答必须以 `{` 字符开始，并以 `}` 字符结束。**
3.  **绝对不要在JSON的外部添加 ```json 或 ``` 这样的Markdown标记。** 这是一个严格的禁令。
4.  该JSON对象**必须只包含** `positive_prompt` 和 `negative_prompt` 这两个键。
5.  **请特别注意**回忆中提到的时代背景（如昭和、70年代等），并在`positive_prompt`中融入该时代特有的服装、建筑、物品和氛围，以增强真实感。

请严格学习并模仿以下范例的转换模式：

---

**【范例1】**

* **输入回忆 (Input):**
    `私が子どもの頃は、粉ミルクの給食をアルミのお盆で食べてたんだよ。`
* **输出JSON (Output):**
    ```json
    {
      "positive_prompt": "Photorealistic, nostalgic, Showa-era photograph of a Japanese school lunch. In a classroom with authentic wooden floors and desks from the 1950s, a young child wearing simple, period-appropriate clothing is sitting and eating from a worn aluminum tray, with powdered milk served. The lighting is soft and natural. The atmosphere is quiet and simple. 35mm film photo style, with subtle grain.",
      "negative_prompt": "ugly, deformed, noisy, blurry, distorted, low resolution, signature, watermark, text, anime, cartoon, 3D render, painting, drawing, CGI, unnatural, modern elements."
    }
    ```

---

**【范例2】**

* **输入回忆 (Input):**
    `学生時代、私はデモに参加し、政治について熱く語り合ったものです。`
* **输出JSON (Output):**
    ```json
    {
      "positive_prompt": "An authentic, photorealistic black and white photograph capturing the fervor of student protests in 1970s Japan. A group of young students with determined, realistic faces and period-specific hairstyles and clothing are marching together on a city street. The image must have a high-contrast, grainy texture, as if shot on vintage high-speed film, evoking a sense of historical significance.",
      "negative_prompt": "ugly, deformed, noisy, blurry, distorted, low resolution, signature, watermark, text, anime, cartoon, 3D render, painting, drawing, CGI, unnatural, color, modern vehicles."
    }
    ```

---

**【范例3】**

* **输入回忆 (Input):**
    `孫が遊びに来るときは、いつも「たべっ子どうぶつ」を準備して待っているんです。`
* **输出JSON (Output):**
    ```json
    {
      "positive_prompt": "A warm, heartwarming, and extremely photorealistic photo capturing a precious family moment in a cozy Japanese living room. An elderly grandparent, with a gentle and loving expression on their face, is sitting at a low table. They are carefully arranging 'Tabekko Doubutsu' animal biscuits onto a small plate. Leaning on the table right next to them, two small grandchildren watch with excitement and joyful anticipation. The room is bathed in warm afternoon sunlight. The image must look like a real, high-quality photograph, rich in authentic detail and emotion.",
      "negative_prompt": "ugly, deformed, noisy, blurry, distorted, grainy, low resolution, signature, watermark, text, anime, cartoon, 3D render, painting, drawing, CGI, unnatural."
    }
    ```

---

现在，你已经学习了如何生成包含时代背景、正负提示语的JSON对象。请严格按照上面的范例，处理我提供的新回忆。

**【新的输入回忆】**

"""
# 允许的负面关键词白名单
# _ALLOWED_NEG = {
#     "duplicate", "extra", "blur", "blurry", "low", "lowres", "low-res",
#     "text", "watermark", "signature", "harsh", "shadow", "urban",
#     "modern", "cropped", "disfigured", "deformed", "multiple"
# }

# def _sanitize_negative(raw_neg: str) -> str:
#     """
#     只保留视觉/技术缺陷相关的词。
#     """
#     if not raw_neg:
#         return ""
#     out = []
#     for part in raw_neg.split(","):
#         token = part.strip().lower()
#         if any(tok in token for tok in _ALLOWED_NEG):
#             out.append(token)
#     return ", ".join(out)

# ---------------------------------------------------------------------
# 1) 把记忆文本 → positive_prompt / negative_prompt
# ---------------------------------------------------------------------
async def _craft_prompts(memory_text: str) -> Dict[str, str]:
    loop = asyncio.get_running_loop()

    def _call_llm() -> Dict[str, str]:
        rsp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _CREATIVE_SYS_PROMPT},
                {"role": "user", "content": memory_text},
            ],
            temperature=0.7,
        )
        try:
            return json.loads(rsp.choices[0].message.content)
        except Exception:
            logger.error("LLM 返回内容无法解析为 JSON", raw=rsp.choices[0].message.content)
            raise

    try:
        return await loop.run_in_executor(None, _call_llm)
    except Exception as exc:
        logger.exception("生成图像 Prompt 失败")
        raise APIError("解析记忆文本失败，请稍后再试。") from exc

# ---------------------------------------------------------------------
# 2) 用 DALL·E 3 生成图像
# ---------------------------------------------------------------------
async def _generate_image(pos_prompt: str, neg_prompt: str, *,
                          n: int = 1, size: str = "1024x1024") -> List[Path]:
    # DALL·E 不支持单独 negative_prompt；用 --no 语法拼接
    full_prompt = f"{pos_prompt} --no {neg_prompt}" if neg_prompt else pos_prompt

    loop = asyncio.get_running_loop()

    def _call_dalle():
        return openai_client.images.generate(
            model="dall-e-3",
            prompt=full_prompt,
            n=n,
            size=size,
        )

    try:
        rsp = await loop.run_in_executor(None, _call_dalle)
    except Exception as exc:
        logger.exception("DALL·E 调用失败")
        raise APIError("生成图像失败，请稍后再试。") from exc

    # 下载并保存图片
    paths: List[Path] = []
    for idx, data in enumerate(rsp.data):
        url = data.url
        img = requests.get(url, timeout=60)
        img.raise_for_status()
        fname = IMAGE_DIR / f"memory_{_dt.datetime.now():%Y%m%d_%H%M%S}_{idx}.png"
        fname.write_bytes(img.content)
        paths.append(fname)

    return paths

# ---------------------------------------------------------------------
# 3) 对外高层接口
# ---------------------------------------------------------------------
async def memory_to_image(memory_text: str, *, n: int = 1,
                          size: str = "1024x1024") -> Path:
    """
    高层接口：输入记忆文本 → 返回首张图片本地路径
    """
    prompts = await _craft_prompts(memory_text)
    pos_prompt = prompts.get("positive_prompt", "")
    neg_prompt = prompts.get("negative_prompt", "")
    # neg_prompt = _sanitize_negative(prompts.get("negative_prompt", ""))
    images = await _generate_image(pos_prompt, neg_prompt, n=n, size=size)

    if not images:
        raise APIError("生成图像失败，请稍后再试。")

    logger.info("Image generated", positive_prompt=pos_prompt, negative_prompt=neg_prompt)
    return images[0]           # 仅返回第一张

__all__ = [
    "fetch_posts",
    "summarize",
    "memory_to_image",
]