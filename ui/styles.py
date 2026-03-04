"""
UI Styles

애플리케이션에서 사용하는 색상, 폰트, ttk 스타일을 정의하는 모듈이다.
UI 스타일을 중앙에서 관리하여 일관된 디자인을 유지하고
스타일 변경 시 유지보수를 쉽게 하기 위한 목적을 가진다.
"""

from tkinter import ttk


# ==============================
# Color Constants
# ==============================

PRIMARY_COLOR = "#2C7BE5"
SECONDARY_COLOR = "#6C757D"
SUCCESS_COLOR = "#28A745"
WARNING_COLOR = "#DC3545"
INFO_COLOR = "#0D6EFD"

BG_COLOR = "#F5F7FA"
CARD_COLOR = "#FFFFFF"

TXT_COLOR = "#212529"
TXT_HOVER_COLOR = "#1A73E8"


# ==============================
# Style Setup
# ==============================

def setup_styles(root):
    """
    ttk 스타일을 초기화한다.

    Parameters
    ----------
    root : tk.Tk
        애플리케이션 루트 위젯
    """

    style = ttk.Style(root)

    # 기본 테마 설정
    try:
        style.theme_use("clam")
    except:
        pass

    # ==============================
    # Frame Styles
    # ==============================

    style.configure("Box.TFrame", background=CARD_COLOR, relief="flat")

    # ==============================
    # Button Styles
    # ==============================

    style.configure("Primary.TButton", padding=6)

    # ==============================
    # Entry Styles
    # ==============================

    style.configure("TEntry", padding=4)

    # ==============================
    # Combobox Styles
    # ==============================

    style.configure("White.TCombobox", padding=3)