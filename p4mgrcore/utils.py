"""
ユーティリティ関数群
メモリ効率とパフォーマンスを重視した実装
"""

from p4mgrcore.constants import COLOR_CACHE


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """
    16進数カラーコードをRGBタプルに変換
    キャッシュを使用してパフォーマンスを向上
    """
    if hex_color in COLOR_CACHE:
        return COLOR_CACHE[hex_color]

    hex_color = hex_color.lstrip("#")

    if len(hex_color) == 3:
        hex_color = "".join([c * 2 for c in hex_color])

    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        result = (r, g, b)

        if len(COLOR_CACHE) < 256:
            COLOR_CACHE[hex_color] = result

        return result
    except (ValueError, IndexError):
        return (255, 255, 255)


def clamp(value: int, min_value: int = 0, max_value: int = 255) -> int:
    """値を指定範囲内に制限"""
    return max(min_value, min(value, max_value))


def get_text_bounds(text: str, font_size: int) -> tuple[int, int]:
    """
    テキストの概算サイズを取得
    実際のフォント計測を避けて高速化
    """
    char_width = int(font_size * 0.6)
    char_height = font_size
    return (len(text) * char_width, char_height)


_scroll_positions_cache = {}


def calculate_scroll_positions(
    text_width: int, canvas_width: int, scroll_speed: int = 2
) -> list:
    """
    スクロール位置のリストを事前計算
    キャッシュを使用してメモリ使用量を削減
    """
    cache_key = (text_width, canvas_width, scroll_speed)

    if cache_key in _scroll_positions_cache:
        return _scroll_positions_cache[cache_key]

    positions = []
    x = canvas_width
    end_x = -text_width

    while x > end_x:
        positions.append(x)
        x -= scroll_speed

    if len(_scroll_positions_cache) < 50:
        _scroll_positions_cache[cache_key] = positions

    return positions
