"""
UI Styles

애플리케이션에서 사용하는 색상, 폰트, ttk 스타일을 정의하는 모듈이다.
UI 스타일을 중앙에서 관리하여 일관된 디자인을 유지하고
스타일 변경 시 유지보수를 쉽게 하기 위한 목적을 가진다.
"""

from tkinter import ttk
import tkinter.font as tkfont

# ==============================
# Color Constants
# ==============================
PRIMARY_COLOR = "#2C7BE5"
SECONDARY_COLOR = "#6C757D"
SUCCESS_COLOR = "#28A745"
WARNING_COLOR = "#DC3545"
INFO_COLOR = "#0D6EFD"

BG_COLOR = "#EEEEEE"
CARD_COLOR = "#FFFFFF"

TXT_COLOR = "#212529"
TXT_HOVER_COLOR = "#1A73E8"

BTN_HOVER_COLOR = "#E5F1FB"

ACTIVE_BORDER_COLOR = "#2C7BE5"

SELECTED_BG_COLOR = "#2C7BE5"
SELECTED_FG_COLOR = "#FFFFFF"

# ==============================
# Style Setup
# ==============================

def setup_styles(app):
    """
    ttk 스타일을 초기화한다.

    Parameters
    ----------
    root : tk.Tk
        애플리케이션 루트 위젯
    """

    style = ttk.Style()

    app.root.option_add("*Entry.selectBackground", SELECTED_BG_COLOR)
    app.root.option_add("*Entry.selectForeground", SELECTED_FG_COLOR)
    app.root.option_add("*Entry.insertBackground", TXT_COLOR)

    # 기본 테마 설정
    try:
        style.theme_use("clam")
    except:
        pass

    # ==============================
    # Font Styles
    # ==============================
    app.font = tkfont.Font(family="맑은 고딕", size=13)
    app.label_font = tkfont.Font(family="맑은 고딕", size=10)
    app.small_font = tkfont.Font(family="맑은 고딕", size=8)
    app.large_font = tkfont.Font(family="맑은 고딕", size=15)

    # ==============================
    # Frame Styles
    # ==============================
    style.configure("TFrame", borderwidth=0, relief="flat")
    style.configure("BOX.TFrame", background=BG_COLOR, borderwidth=1, relief="solid")
    # style.configure("TLabelframe", background=BG_COLOR)
    # style.configure("TLabelframe.Label", background=BG_COLOR, font=app.label_font)


    # ==============================
    # Button Styles
    # ==============================
    style.configure("Primary.TButton", padding=6)
    style.map("Primary.TButton", background=[("active", BTN_HOVER_COLOR)], bordercolor=[("active", ACTIVE_BORDER_COLOR)])

    # ==============================
    # Entry Styles
    # ==============================
    style.configure("TEntry", background=BG_COLOR)
    style.map("TEntry", bordercolor=[("focus", ACTIVE_BORDER_COLOR)], lightcolor=[("focus", ACTIVE_BORDER_COLOR)], darkcolor=[("focus", ACTIVE_BORDER_COLOR)])


    # ==============================
    # Treeview Styles
    # ==============================
    style.configure("Treeview", font=app.font, background="white", fieldbackground="white", rowheight=25)
    style.map("Treeview", background=[("selected", "#DCEBFF")], foreground=[("selected", "black")])
    style.configure("Treeview.Heading", font=("맑은 고딕", 12, "bold"), background="#ffffff", borderwidth=0, relief="flat")
    style.map("Treeview.Heading", background=[("active", "#DADADA")])

    # ==============================
    # Combobox Styles
    # ==============================
    style.configure("White.TCombobox", padding=3)