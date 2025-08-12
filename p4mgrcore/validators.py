"""
設定値の軽量検証モジュール
ラズベリーパイでのパフォーマンスを考慮し、最小限の検証のみ実施
"""

from typing import Any


class ConfigValidator:
    """設定値の軽量検証クラス"""

    @staticmethod
    def validate_display_config(config: dict[str, Any]) -> str | None:
        """
        表示設定の基本検証
        エラーがあればエラーメッセージを返す、なければNone
        """
        if not isinstance(config, dict):
            return "設定はdictionary形式である必要があります"

        # 必須フィールドのチェック
        if "type" not in config:
            return "表示タイプ(type)が指定されていません"

        display_type = config["type"]
        if display_type not in ["dest", "textNsc", "textScr"]:
            return f"不明な表示タイプ: {display_type}"

        # タイプ別の必須フィールドチェック
        if display_type == "dest":
            if "destination" not in config:
                return "destination設定が必要です"
            if not isinstance(config["destination"], dict):
                return "destinationはdictionary形式である必要があります"
            if "text" not in config["destination"]:
                return "destination.textが必要です"

        elif display_type in ["textNsc", "textScr"]:
            if "txt" not in config:
                return "txt設定が必要です"
            if not isinstance(config["txt"], dict):
                return "txtはdictionary形式である必要があります"
            if "text" not in config["txt"]:
                return "txt.textが必要です"

        return None

    @staticmethod
    def validate_color(color: str) -> bool:
        """
        色コードの簡易検証
        """
        if not isinstance(color, str):
            return False

        # #を削除
        color = color.lstrip("#")

        # 3文字または6文字の16進数
        if len(color) not in [3, 6]:
            return False

        # 16進数文字のみ
        try:
            int(color, 16)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_matrix_config(config: dict[str, Any]) -> str | None:
        """
        RGBMatrix設定の検証
        """
        if not isinstance(config, dict):
            return "Matrix設定はdictionary形式である必要があります"

        # 数値フィールドの範囲チェック
        numeric_fields = {
            "rows": (8, 64),
            "cols": (8, 128),
            "chain_length": (1, 8),
            "brightness": (1, 100),
        }

        for field, (min_val, max_val) in numeric_fields.items():
            if field in config:
                value = config[field]
                if not isinstance(value, int):
                    return f"{field}は整数である必要があります"
                if value < min_val or value > max_val:
                    return f"{field}は{min_val}から{max_val}の範囲である必要があります"

        return None


def quick_validate_config(config: dict[str, Any]) -> list[str]:
    """
    設定全体の高速検証
    エラーメッセージのリストを返す
    """
    errors = []

    if not config:
        errors.append("設定が空です")
        return errors

    # displays設定の検証
    if "displays" in config:
        displays = config["displays"]
        if not isinstance(displays, dict):
            errors.append("displaysはdictionary形式である必要があります")
        else:
            for key, display_config in displays.items():
                error = ConfigValidator.validate_display_config(display_config)
                if error:
                    errors.append(f"表示設定 '{key}': {error}")

    # matrix設定の検証（あれば）
    if "matrix" in config:
        error = ConfigValidator.validate_matrix_config(config["matrix"])
        if error:
            errors.append(f"Matrix設定: {error}")

    return errors
