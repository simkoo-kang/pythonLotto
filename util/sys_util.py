import sys
import tkinter as tk

# Windows 환경일 때만 IME 조회를 위한 ctypes 임포트
if sys.platform == "win32":
    import ctypes


class Sys:

    @staticmethod
    @DeprecationWarning
    def check_ime_status(event=None):
        """ 정상 작동 안함 """
        try:
            # [수정] 메인창 핸들이 아니라, 현재 OS 상에서 전역 포커스를 가진 윈도우 핸들을 가져옵니다.
            user32 = ctypes.WinDLL("user32")
            hwnd = user32.GetFocus() 
            
            if not hwnd:
                return False

            imm32 = ctypes.WinDLL("imm32")
            h_ime = imm32.ImmGetContext(hwnd)

            dw_mode = ctypes.c_ulong()
            dw_sentence = ctypes.c_ulong()
            imm32.ImmGetConversionStatus(h_ime, ctypes.byref(dw_mode), ctypes.byref(dw_sentence))
            imm32.ImmReleaseContext(hwnd, h_ime)

            # dw_mode가 1(또는 홀수)이면 한글 모드입니다.
            return True if 0 < dw_mode.value & 0x0001 else False

        except Exception:
            print("상태를 가져올 수 없습니다.")
        
        return False

    @staticmethod
    def check_caps_lock(event=None) -> bool:
        """ return True if Caps Lock is On else False"""
        if event is None:
            if sys.platform == "win32":
                # 0x14는 Caps Lock의 가상 키 코드(VK_CAPITAL)입니다.
                return True if 0 < ctypes.WinDLL("User32.dll").GetKeyState(0x14) & 0x0001 else False
            # unreachable
        return (event.state & 0x0002) != 0


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    print("check_caps_lock", Sys.check_caps_lock())
    print("check_ime_status", Sys.check_ime_status())
    