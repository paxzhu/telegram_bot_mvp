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

from tg_bot.config import APIFY_TOKEN, GOOGLE_API_KEY, STABILITY_API_KEY
from tg_bot.exceptions import APIError

logger = structlog.get_logger("core")

# 输出图片保存目录 ----------------------------------------------------
IMAGE_DIR = Path(__file__).resolve().parent / "generated_images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

# 初始化 SDK ---------------------------------------------------------
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
        f"and respond in one natural, concise {lang_code} sentence. \n\n"
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
_SYS_PROMPT = (
    "You are an assistant that reads a user\'s memory description in **any language** and outputs a compact JSON object. "
    "The JSON **must only** contain the keys: subject, secondary_subjects, location, time_of_day, season, action, mood, "
    "weather, style, color_palette, camera. Include a key **only** if it is explicitly mentioned or strongly implied. "
    "Translate every value you output into clear, natural **English**, even if the input text is not English. "
    "Keep the whole JSON within 50 tokens and output **nothing but the JSON**."
)

_DEFAULT_PROMPT_VARS = {
    "style": "photo‑realistic, 85 mm lens, shallow depth of field",
    "color_palette": "natural, vibrant greens, soft warm light",
    "time_of_day": "golden hour",
}

async def _extract_key_elements(text: str) -> Dict:
    loop = asyncio.get_running_loop()
    try:
        rsp = await loop.run_in_executor(
            None,
            lambda: _text_model.generate_content(
                contents=[_SYS_PROMPT, text],
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                ),
            )
        )
        return json.loads(rsp.text)
    except Exception as exc:
        logger.exception("Gemini 提取元素失败")
        raise APIError("无法解析记忆文本，请稍后再试。") from exc

def _enrich_elements(elems: Dict) -> Dict:
    enriched = {**_DEFAULT_PROMPT_VARS, **elems}
    if "season" not in enriched:
        month = _dt.datetime.now().month
        enriched["season"] = (
            "summer" if 5 <= month <= 8 else
            "autumn" if 9 <= month <= 11 else
            "winter" if month <= 2 else "spring"
        )
    return enriched

def _build_prompt(e: Dict) -> str:
    sec = f", {', '.join(e['secondary_subjects'])}" if e.get("secondary_subjects") else ""
    tpl = (
        "Ultra photo‑realistic | {subject}{sec} | {location} | {time_of_day}, {season} | "
        "{mood} | {weather} | {style} | {color_palette} | {camera}"
    )
    return tpl.format(
        sec=sec,
        **{k: e.get(k, "") for k in [
            "subject", "location", "time_of_day", "season", "mood", "weather", "style", "color_palette", "camera"
        ]},
    )

async def _generate_image(prompt: str, *, n: int = 1, size: str = "1024x1024") -> List[str]:
    if not STABILITY_API_KEY:
        raise APIError("未配置 STABILITY_API_KEY")

    width, height = map(int, size.split("x"))
    url = url = f"https://api.stability.ai/v1/generation/{ENGINE}/text-to-image"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {STABILITY_API_KEY}",
    }
    payload = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 7,
        "height": height,
        "width": width,
        "samples": n,
        "steps": 30,
    }

    loop = asyncio.get_running_loop()

    def _post():
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code >= 400:
            print(">>>", resp.text)
        resp.raise_for_status()
        return resp.json()

    try:
        data = await loop.run_in_executor(None, _post)
    except Exception as exc:
        logger.exception("Stability AI 调用失败")
        raise APIError("生成图像失败，请稍后再试。") from exc

    paths: List[str] = []
    for idx, art in enumerate(data.get("artifacts", [])):
        fname = IMAGE_DIR / f"memory_{_dt.datetime.now():%Y%m%d_%H%M%S}_{idx}.png"
        with open(fname, "wb") as f:
            f.write(base64.b64decode(art["base64"]))
        paths.append(fname)
    return paths

async def memory_to_image(memory_text: str, *, n: int = 1, size: str = "1024x1024") -> str:
    """高层接口：输入记忆文本 → 返回首张图片路径。"""
    elems = await _extract_key_elements(memory_text)
    full  = _enrich_elements(elems)
    prompt = _build_prompt(full)
    images = await _generate_image(prompt, n=n, size=size)
    if not images:
        raise APIError("生成图像失败，请稍后再试。")
    logger.info("Image generated", prompt=prompt)
    return images[0]  # 仅返回第一张

__all__ = [
    "fetch_posts",
    "summarize",
    "memory_to_image",
]