"""Assert 自有视觉属性工具；不加载其他项目代码。"""
import numpy as np
from PIL import Image

DHASH_EDGE = 8

def rgb_to_color_name(r: float, g: float, b: float) -> tuple[str, str]:
    """与 knowledge_expander 同口径的中文/英文色名映射（避免依赖单例的随机采样）。"""
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    max_c, min_c = max(r, g, b), min(r, g, b)
    sat = (max_c - min_c) / (max_c + 1e-5)
    if sat < 0.14:
        if lum < 50:
            return "浓郁曜石黑", "Obsidian Black"
        if lum < 120:
            return "深沉石板灰", "Slate Gray"
        if lum < 200:
            return "质感中性灰", "Neutral Heather Gray"
        return "纯净明亮白", "Pure Crisp White"
    if r > g * 1.35 and r > b * 1.35:
        return ("典雅酒红/深绯", "Deep Burgundy Red") if lum < 110 else ("鲜明中国红/赤焰红", "Vibrant Scarlet Red")
    if g > r * 1.25 and g > b * 1.25:
        return ("沉稳墨绿/橄榄绿", "Forest Olive Green") if lum < 120 else ("清爽翠绿/薄荷绿", "Vivid Emerald Green")
    if b > r * 1.25 and b > g * 1.1:
        return ("深邃海军蓝/藏青", "Deep Navy Blue") if lum < 115 else ("明媚皇家蓝/天青", "Vibrant Royal Blue")
    if r > 160 and g > 130 and b < 90:
        return "辉煌金黄/琥珀黄", "Golden Amber Yellow"
    if r > 160 and g > 75 and b < 70:
        return "活力热烈橙", "Vivid Energetic Orange"
    if r > 120 and b > 120 and g < 100:
        return "神秘魅惑紫", "Mystic Royal Purple"
    if r > 160 and b > 130 and g > 110:
        return "浪漫樱花粉", "Soft Blossom Pink"
    return "复合混色调", "Multi-Color Composite"


def geometry_from_aspect(aspect: float) -> tuple[str, str]:
    if aspect >= 1.6:
        return "横向宽幅扁平矩形构型", "Horizontal Widescreen Layout"
    if aspect <= 0.65:
        return "纵向立式纤细长条构型", "Tall Vertical Banner Proportion"
    if 0.90 <= aspect <= 1.10:
        return "正方形/对称正圆同心圆构型", "Square / Concentric Circular Geometry"
    return "标准 4:3 / 3:2 传统旗帜与徽章比例", "Classic 3:2 / 4:3 Aspect Ratio"


def dhash64(img_rgba: Image.Image) -> str:
    """感知哈希：白底合成后灰度 9x8 相邻比较，返回 16 位十六进制。"""
    white = Image.new("RGBA", img_rgba.size, (255, 255, 255, 255))
    white.alpha_composite(img_rgba)
    gray = white.convert("L").resize((DHASH_EDGE + 1, DHASH_EDGE), Image.Resampling.LANCZOS)
    arr = np.asarray(gray, dtype=np.int16)
    bits = (arr[:, 1:] > arr[:, :-1]).reshape(-1)
    value = 0
    for bit in bits:
        value = (value << 1) | int(bool(bit))
    return f"{value:016x}"


def hamming(a: str, b: str) -> int:
    return (int(a, 16) ^ int(b, 16)).bit_count()
