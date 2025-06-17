import random, pathlib

_SAMPLE_DIR = pathlib.Path(__file__).with_suffix("").parent / "assets" / "samples"

def generate_image_path(_: str) -> pathlib.Path:
    """
    伪造图像：随机挑选 samples 目录下的 jpg。
    参数 _ (text) 保留接口兼容后续 Stable Diffusion 替换。
    """
    pics = list(_SAMPLE_DIR.glob("*.jpg"))
    if not pics:
        raise RuntimeError("No sample images found in assets/samples/")
    return random.choice(pics)
