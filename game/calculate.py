import math
import re
import tkinter as tk
from tkinter import messagebox


def on_button_click(char):
    """버튼 클릭 시 입력창에 글자를 추가하거나 기능을 수행합니다."""
    current = entry.get()

    if char == "C":
        entry.delete(0, tk.END)
    elif char == "◀":
        entry.delete(len(current) - 1, tk.END)
    elif char == "=":
        calculate()
    else:
        entry.insert(tk.END, char)


def calculate():
    """입력된 수식을 파이썬 math 규칙에 맞게 변환하여 계산합니다."""
    expr = entry.get()

    # 1. 괄호가 없는 √, sin, cos, tan, log 뒤의 숫자나 문자를 찾아 자동으로 괄호 씌우기
    # 예: √4 -> √(4), sinπ -> sin(π)
    functions = ["√", "sin", "cos", "tan", "log"]
    for func in functions:
        # 함수 이름 뒤에 바로 숫자, 소수점, 또는 π가 오는 패턴을 찾아 괄호 처리
        expr = re.sub(
            rf"{func}([0-9.π]+)", rf"{func}(\1)", expr
        )  # 저장 시 줄바꿈 방지 위해 한 줄 유지

    # 2. 파이썬 math 라이브러리 코드로 치환
    expr = expr.replace("×", "*").replace("÷", "/")
    expr = expr.replace("^", "**")
    expr = expr.replace("√", "math.sqrt")
    expr = expr.replace("sin", "math.sin")
    expr = expr.replace("cos", "math.cos")
    expr = expr.replace("tan", "math.tan")
    expr = expr.replace("log", "math.log10")
    expr = expr.replace("π", str(math.pi))

    try:
        result = eval(expr)

        if isinstance(result, float) and result.is_integer():
            result = int(result)
        elif isinstance(result, float):
            result = round(result, 6)

        entry.delete(0, tk.END)
        entry.insert(tk.END, str(result))
    except Exception:
        messagebox.showerror(
            "오류", "잘못된 수식입니다. 괄호나 기호를 확인하세요."
        )


# --- GUI 화면 구성 ---
root = tk.Tk()
root.title("공학용 수식 계산기")
root.geometry("400x500")
root.resizable(False, False)

# 1. 수식 입력 및 결과 출력 창
entry = tk.Entry(
    root, font=("맑은 고딕", 20), justify="right", bd=10, relief=tk.FLAT
)
entry.pack(fill=tk.BOTH, ipadx=8, ipady=15, padx=10, pady=10)

# 2. 버튼 레이아웃 구조 (저장 시 세로 방지를 위해 주석 유지)
# fmt: off
buttons = [
    ["sin", "cos", "tan", "log"],
    ["^", "√", "π", "◀"],
    ["(", ")", "÷", "C"],
    ["7", "8", "9", "×"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "+"],
    ["0", ".", "=", ""]
]
# fmt: on

# 버튼을 배치할 프레임 생성
button_frame = tk.Frame(root)
button_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# grid 방식을 사용하여 바둑판 모양으로 배치
for row_idx, row in enumerate(buttons):
    for col_idx, text in enumerate(row):
        if text == "":
            continue

        # 버튼 색상 및 스타일 지정
        if text in ["=", "C", "◀"]:
            bg_color = "#ff9500"  # 주황색 (기능 버튼)
            fg_color = "white"
        elif text in ["+", "-", "×", "÷", "^", "√", "sin", "cos", "tan", "log"]:
            bg_color = "#b3b3b3"  # 회색 (연산자)
            fg_color = "black"
        else:
            bg_color = "#e0e0e0"  # 연한 회색 (숫자)
            fg_color = "black"

        # 0 버튼은 가로로 두 칸 차지하도록 설정
        colspan = 2 if text == "0" else 1

        btn = tk.Button(
            button_frame,
            text=text,
            font=("맑은 고딕", 14),
            bg=bg_color,
            fg=fg_color,
            bd=1,
            command=lambda t=text: on_button_click(t),
        )
        btn.grid(
            row=row_idx,
            column=col_idx,
            columnspan=colspan,
            sticky="nsew",
            padx=2,
            pady=2,
        )

# grid 내부 비율을 똑같이 맞춰 창 크기에 맞게 조절되도록 설정
for i in range(7):
    button_frame.rowconfigure(i, weight=1)
for i in range(4):
    button_frame.columnconfigure(i, weight=1)

root.mainloop()
