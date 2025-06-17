import random, pathlib

_SAMPLE_DIR = pathlib.Path(__file__).with_suffix("").parent / "assets" / "samples"

def generate_image_path(_: str) -> pathlib.Path:
    """
    随机挑选 samples 目录下的 jpg。
    """
    pics = list(_SAMPLE_DIR.glob("*.png"))
    if not pics:
        raise RuntimeError("No sample images found in assets/samples/")
    return random.choice(pics)
