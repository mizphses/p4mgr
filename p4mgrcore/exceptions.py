"""
P4Mgr用の例外クラス定義
軽量で明確なエラーハンドリングのため
"""


class P4MgrError(Exception):
    """P4Mgrの基底例外クラス"""

    pass


class ConfigError(P4MgrError):
    """設定関連のエラー"""

    pass


class DisplayError(P4MgrError):
    """表示処理関連のエラー"""

    pass


class InputDeviceError(P4MgrError):
    """入力デバイス関連のエラー"""

    pass


class FontError(P4MgrError):
    """フォント関連のエラー"""

    pass


class MatrixError(P4MgrError):
    """RGBMatrix関連のエラー"""

    pass
