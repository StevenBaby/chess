import win32gui
import win32ui
from ctypes import windll
from PIL import Image


def capture(window_name):

    # https://learn.microsoft.com/en-us/windows/win32/api/shellscalingapi/nf-shellscalingapi-setprocessdpiawareness
    PROCESS_PER_MONITOR_DPI_AWARE = 2
    windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)

    hwnd = win32gui.FindWindow(None, window_name)
    if not hwnd:
        return None

    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    w = right - left
    h = bot - top

    # https://timgolden.me.uk/pywin32-docs/win32gui.html
    # returns the device context (DC) for the entire window,
    # including title bar, menus, and scroll bars.
    hwndDC = win32gui.GetWindowDC(hwnd)

    # Creates a PyCDC object from an integer handle.
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)

    # Creates a memory DC compatible with this DC.
    saveDC = mfcDC.CreateCompatibleDC()

    # Create a bitmap object.
    saveBitMap = win32ui.CreateBitmap()

    # Creates a bitmap compatible with the specified device context.
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

    # Selects an object into the DC.
    saveDC.SelectObject(saveBitMap)

    # Change the line below depending on whether you want the whole window
    # or just the client area.
    # result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)
    windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)

    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)

    # release object
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    return im
