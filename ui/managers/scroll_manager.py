"""
ScrollManager

애플리케이션 전체의 마우스 휠 스크롤 이벤트를 관리하는 매니저 클래스이다.
전역 마우스 휠 이벤트를 감지하고, 등록된 대상(target) 위젯에게
스크롤 처리를 위임하거나 기본 Canvas 스크롤을 수행한다.

이 클래스는 다음을 담당한다:
- 전역 마우스 휠 이벤트 감지
- 특정 UI 컴포넌트로 스크롤 이벤트 위임
- 스크롤 대상이 없는 경우 기본 Canvas 스크롤 수행
- Windows / Linux 환경의 마우스 휠 이벤트 처리
"""

class ScrollManager:
    def __init__(self, root, canvas):
        self.root = root
        self.canvas = canvas
        root.bind_all("<MouseWheel>", self.on_mousewheel)
        root.bind_all("<Button-4>", self.on_mousewheel)
        root.bind_all("<Button-5>", self.on_mousewheel)

        self.targets = []

    def register(self, target):
        """
        target은 아래 메서드를 가져야 함
        - is_inside(widget) -> bool
        - scroll(event)
        """
        self.targets.append(target)

    def on_mousewheel(self, event):
        try:
            widget = event.widget

            if not hasattr(widget, "winfo_containing"):
                widget = self.root.winfo_containing(event.x_root, event.y_root)
                if widget is None:
                    return

            # 먼저 등록된 target에게 위임
            for target in self.targets:
                if target.is_inside(widget):
                    target.scroll(event)
                    return

            # 아무도 안 받으면 전체 스크롤
            self._scroll_canvas(event)
        except Exception:
            return

    def _scroll_canvas(self, event):
        if event.delta:
            self.canvas.yview_scroll(int(-event.delta / 120), "units")
        elif event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
