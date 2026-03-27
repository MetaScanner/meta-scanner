"""
MetaCollector Application Entry Point

이 파일은 MetaCollector 프로그램의 실행 진입점이다.
Tkinter 기반 GUI 애플리케이션을 시작하며,
루트 윈도우를 생성하고 MetaCollector 앱을 초기화한 후
메인 이벤트 루프를 실행한다.
"""

import tkinter as tk
from app import MetaCollector

def main():

    root=tk.Tk()
    app = MetaCollector(root)
    root.mainloop()

if __name__ == "__main__":
    main()