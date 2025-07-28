import cv2
import mediapipe as mp
import math
import time
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController
import pyautogui
import ctypes

pyautogui.FAILSAFE = False
mouse = MouseController()
keyboard = KeyboardController()
smoothed_dx, smoothed_dy = 0, 0
alpha = 0.2
SENSITIVITY = 2.5
holding_click = False
walking = False
prev_hand_pos = None

PUL = ctypes.POINTER(ctypes.c_ulong)

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("mi", MouseInput), ("ki", KeyBdInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("ii", Input_I)]

def move_mouse_raw(dx, dy):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.mi = MouseInput(dx, dy, 0, 0x0001, 0, ctypes.pointer(extra))
    command = Input(ctypes.c_ulong(0), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))

def press_key(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(wVk=hexKeyCode, wScan=0, dwFlags=0, time=0, dwExtraInfo=ctypes.pointer(extra))
    command = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.byref(command), ctypes.sizeof(command))

def release_key(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(wVk=hexKeyCode, wScan=0, dwFlags=0x0002, time=0, dwExtraInfo=ctypes.pointer(extra))
    command = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.byref(command), ctypes.sizeof(command))

def is_fist(lm): return all(lm[t][2] > lm[p][2] for t, p in [(8,6),(12,10),(16,14),(20,18)])
def is_open_palm(lm): return all(lm[t][2] < lm[p][2] for t, p in [(8,6),(12,10),(16,14),(20,18)])
def is_index_up_only(lm): return lm[8][2] < lm[6][2] and all(lm[t][2] > lm[p][2] for t,p in [(12,10),(16,14),(20,18)])
def is_pinky_only(lm): return lm[20][2] < lm[18][2] and all(lm[t][2] > lm[p][2] for t,p in [(8,6),(12,10),(16,14)])
def is_thumb_touching_pinky(lm, threshold=40):
    x1, y1 = lm[4][1], lm[4][2]
    x2, y2 = lm[20][1], lm[20][2]
    return math.hypot(x2 - x1, y2 - y1) < threshold
def is_walk_forward(lm):
    return (
        lm[8][2] < lm[6][2] and lm[12][2] < lm[10][2] and
        lm[16][2] > lm[14][2] and lm[20][2] > lm[18][2]
    )
def is_thumbs_down(lm):
    return lm[4][2] > lm[2][2]

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)
    h, w, _ = img.shape
    lm_list = []

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            for id, lm in enumerate(hand_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((id, cx, cy))

            if len(lm_list) == 21:
                if is_fist(lm_list) and not holding_click:
                    mouse.press(Button.left)
                    holding_click = True
                    print(" Holding left click")
                elif not is_fist(lm_list) and holding_click:
                    mouse.release(Button.left)
                    holding_click = False
                    print(" Released left click")

                if is_open_palm(lm_list):
                    mouse.click(Button.right)
                    print(" Right click")
                    time.sleep(0.3)

                elif is_index_up_only(lm_list):
                    press_key(0x20)  
                    release_key(0x20)
                    print(" Jump")
                    time.sleep(0.3)

                if is_pinky_only(lm_list):
                    mouse.click(Button.left)
                    print(" Pinky left click")
                    time.sleep(0.3)

                if is_thumbs_down(lm_list):
                    pyautogui.press("e")
                    print("Inventory opened (thumbs down)")
                    time.sleep(0.5)

                if is_walk_forward(lm_list):
                    if not walking:
                        keyboard.press("w")
                        walking = True
                        print("🚶 Walking forward")
                else:
                    if walking:
                        keyboard.release("w")
                        walking = False

                x, y = lm_list[8][1], lm_list[8][2]
                if prev_hand_pos:
                    dx = (x - prev_hand_pos[0]) * SENSITIVITY
                    dy = (y - prev_hand_pos[1]) * SENSITIVITY
                    smoothed_dx = smoothed_dx * (1 - alpha) + dx * alpha
                    smoothed_dy = smoothed_dy * (1 - alpha) + dy * alpha

                    if abs(smoothed_dx) > 1 or abs(smoothed_dy) > 1:
                        move_mouse_raw(int(smoothed_dx), int(smoothed_dy))
                        print(f" Smooth camera dx={int(smoothed_dx)}, dy={int(smoothed_dy)}")

                prev_hand_pos = (x, y)

    else:
        if holding_click:
            mouse.release(Button.left)
            holding_click = False
            print(" Released left click (no hand)")
        if walking:
            keyboard.release("w")
            walking = False
        prev_hand_pos = None

    cv2.imshow("Minecraft Gesture Control", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
