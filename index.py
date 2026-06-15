import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import time
import math
import pyautogui
import ctypes
import screen_brightness_control as sbc
from datetime import datetime

# --- Application Configurations ---
pyautogui.FAILSAFE = False
wScr, hScr = pyautogui.size()

frameR = 130          # Camera reduction box margin
plocX, plocY = 0, 0
clocX, clocY = 0, 0
prev_scroll_y = 0
prev_vol_dist = 0
prev_bright_dist = 0

# Cooldown and gesture triggers timers
last_fist_time = 0
last_macro_time = 0
last_media_time = 0
screenshot_counter = 0 # Timer tracking for 5-finger screenshot hold

# --- Native Windows Volume Keys ---
VK_VOLUME_UP = 0xAF
VK_VOLUME_DOWN = 0xAE

def control_system_volume(action, steps=1):
    for _ in range(steps):
        if action == "up":
            ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 0, 0)
            ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 2, 0)
        elif action == "down":
            ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
            ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 2, 0)

# --- MediaPipe Setup ---
baseOptions = python.BaseOptions(model_asset_path="hand_landmarker.task")
options = vision.HandLandmarkerOptions(base_options=baseOptions, num_hands=1) 
detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)
pTime = 0

# Window Setup for Native Minimize, Maximize, and Fullscreen Capabilities
cv2.namedWindow('Ultimate Virtual Controller HUD', cv2.WINDOW_NORMAL)
is_fullscreen = False

while True:
    ret, frame = cap.read()
    if not ret: break
    
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    
    # Draw sleek holographic corners for the tracking reduction box
    cv2.rectangle(frame, (frameR, frameR), (w - frameR, h - frameR), (80, 80, 80), 1)
    # Top-Left Corner Glow
    cv2.line(frame, (frameR, frameR), (frameR + 20, frameR), (0, 255, 255), 3)
    cv2.line(frame, (frameR, frameR), (frameR, frameR + 20), (0, 255, 255), 3)
    # Top-Right Corner Glow
    cv2.line(frame, (w - frameR, frameR), (w - frameR - 20, frameR), (0, 255, 255), 3)
    cv2.line(frame, (w - frameR, frameR), (w - frameR, frameR + 20), (0, 255, 255), 3)
    # Bottom-Left Corner Glow
    cv2.line(frame, (frameR, h - frameR), (frameR + 20, h - frameR), (0, 255, 255), 3)
    cv2.line(frame, (frameR, h - frameR), (frameR, h - frameR - 20), (0, 255, 255), 3)
    # Bottom-Right Corner Glow
    cv2.line(frame, (w - frameR, h - frameR), (w - frameR - 20, h - frameR), (0, 255, 255), 3)
    cv2.line(frame, (w - frameR, h - frameR), (w - frameR, h - frameR - 20), (0, 255, 255), 3)

    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mpImage = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgbImage)
    result = detector.detect(mpImage)

    mode_text = "SYSTEM: MONITORING"
    hud_val = 0
    hud_type = None 

    if result.hand_landmarks:
        landmarks = result.hand_landmarks[0]
        
        # Extract pixel coordinates of finger tips
        x4, y4 = int(landmarks[4].x * w), int(landmarks[4].y * h)     # Thumb
        x8, y8 = int(landmarks[8].x * w), int(landmarks[8].y * h)     # Index
        x12, y12 = int(landmarks[12].x * w), int(landmarks[12].y * h) # Middle
        x16, y16 = int(landmarks[16].x * w), int(landmarks[16].y * h) # Ring
        x20, y20 = int(landmarks[20].x * w), int(landmarks[20].y * h) # Pinky

        # Basic open state checks using PIP joints
        isIndexUp = landmarks[8].y < landmarks[6].y 
        isMiddleUp = landmarks[12].y < landmarks[10].y
        isRingUp = landmarks[16].y < landmarks[14].y
        isPinkyUp = landmarks[20].y < landmarks[18].y
        
        # Horizontal check for thumb open state
        isThumbUp = landmarks[4].x > landmarks[3].x if landmarks[17].x < landmarks[5].x else landmarks[4].x < landmarks[3].x

        # --- GESTURE 1: ALL FINGERS CLOSED (Fist -> Minimize All / Show Desktop) ---
        if not isIndexUp and not isMiddleUp and not isRingUp and not isPinkyUp and not isThumbUp:
            mode_text = "MACRO: SHOW DESKTOP"
            currentTime = time.time()
            if currentTime - last_fist_time > 1.5:
                pyautogui.hotkey('win', 'd')
                last_fist_time = currentTime
            cv2.circle(frame, (x8, y8), 25, (0, 0, 255), -1)
            screenshot_counter = 0

        # --- GESTURE 2: ALL 5 FINGERS OPEN (Screenshot Capture with holding counter) ---
        elif isIndexUp and isMiddleUp and isRingUp and isPinkyUp and isThumbUp:
            screenshot_counter += 1
            remaining = max(0, 30 - screenshot_counter)
            mode_text = f"CAPTURE: SCREENSHOT IN {int(remaining/10)}s"
            
            # Draw visual scanning circle overlay
            cv2.circle(frame, (w//2, h//2), 40 + (screenshot_counter * 2), (0, 255, 255), 2)
            
            if screenshot_counter >= 30: # Trigger after ~1.5 seconds of sustained hold
                mode_text = "CAPTURE: SAVED!"
                ss = pyautogui.screenshot()
                filename = f"System_Capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                ss.save(filename)
                screenshot_counter = 0
                print(f"System Screenshot saved as: {filename}")
                time.sleep(0.5)

        # --- GESTURE 3: PHONE SIGN (Thumb + Pinky Up -> Media Play/Pause Toggle) ---
        elif isThumbUp and isPinkyUp and not isIndexUp and not isMiddleUp and not isRingUp:
            mode_text = "MEDIA: PLAY / PAUSE"
            currentTime = time.time()
            if currentTime - last_media_time > 1.2: # Cooldown to avoid multi-trigger
                pyautogui.press('playpause')
                last_media_time = currentTime
            cv2.line(frame, (x4, y4), (x20, y20), (0, 255, 0), 3)
            screenshot_counter = 0

        # --- GESTURE 4: ROCK ON SIGN (Alt + Tab Application Switcher Macro) ---
        elif isIndexUp and isPinkyUp and not isMiddleUp and not isRingUp and not isThumbUp:
            mode_text = "MACRO: APP SWITCHER"
            currentTime = time.time()
            if currentTime - last_macro_time > 1.0:
                pyautogui.hotkey('alt', 'tab')
                last_macro_time = currentTime
            screenshot_counter = 0

        # --- MODE 1: VELOCITY-BASED DYNAMIC MOUSE MAPPING (1 Finger Up) ---
        elif isIndexUp and not isMiddleUp and not isRingUp and not isPinkyUp:
            mode_text = "HUD: DYNAMIC MOUSE"
            screenshot_counter = 0
            
            xScr = np.interp(x8, (frameR, w - frameR), (0, wScr))
            yScr = np.interp(y8, (frameR, h - frameR), (0, hScr))
            
            velocity = math.hypot(xScr - plocX, yScr - plocY)
            dynamic_smoothening = np.clip(np.interp(velocity, [1, 50], [15, 3]), 3, 15)

            clocX = plocX + (xScr - plocX) / dynamic_smoothening
            clocY = plocY + (yScr - plocY) / dynamic_smoothening
            
            pyautogui.moveTo(clocX, clocY)
            plocX, plocY = clocX, clocY
            
            # Left Click Visuals & Trigger via Thumb pinch
            left_click_dist = math.hypot(x8 - x4, y8 - y4)
            cv2.line(frame, (x4, y4), (x8, y8), (255, 0, 255), 2)
            if left_click_dist < 30:
                mode_text = "ACTION: LEFT CLICK"
                cv2.circle(frame, ((x4+x8)//2, (y4+y8)//2), 15, (0, 255, 0), -1)
                pyautogui.click()
                time.sleep(0.18)

        # --- MODE 2: WEB SCROLLING & RIGHT CLICK (2 Fingers Up) ---
        elif isIndexUp and isMiddleUp and not isRingUp and not isPinkyUp:
            screenshot_counter = 0
            fingers_dist = math.hypot(x12 - x8, y12 - y8)
            
            if fingers_dist < 45:
                mode_text = "HUD: SCROLL ACTIVE"
                if prev_scroll_y != 0:
                    if prev_scroll_y - y8 > 12: pyautogui.scroll(160)
                    elif y8 - prev_scroll_y > 12: pyautogui.scroll(-160)
                prev_scroll_y = y8
                cv2.circle(frame, (x8, y8), 10, (255, 255, 0), -1)
            else:
                prev_scroll_y = 0
                mode_text = "HUD: READY (RIGHT CLICK)"
                right_click_dist = math.hypot(x12 - x4, y12 - y4)
                cv2.line(frame, (x4, y4), (x12, y12), (255, 0, 0), 2)
                if right_click_dist < 30:
                    mode_text = "ACTION: RIGHT CLICK"
                    cv2.circle(frame, (x12, y12), 15, (0, 255, 255), -1)
                    pyautogui.click(button='right')
                    time.sleep(0.3)

        # --- MODE 3: SYSTEM MASTER VOLUME CONTROL (3 Fingers Up) ---
        elif isIndexUp and isMiddleUp and isRingUp and not isPinkyUp:
            screenshot_counter = 0
            mode_text = "HUD: MASTER VOLUME"
            hud_type = "VOLUME"
            
            vol_dist = math.hypot(x8 - x4, y8 - y4)
            cv2.line(frame, (x4, y4), (x8, y8), (0, 255, 255), 3)
            
            hud_val = int(np.clip(np.interp(vol_dist, [30, 190], [0, 100]), 0, 100))

            if prev_vol_dist != 0:
                diff = vol_dist - prev_vol_dist
                if diff > 7:
                    control_system_volume("up", int(diff / 7))
                    prev_vol_dist = vol_dist
                elif diff < -7:
                    control_system_volume("down", int(abs(diff) / 7))
                    prev_vol_dist = vol_dist
            else:
                prev_vol_dist = vol_dist

        # --- MODE 4: MONITOR BRIGHTNESS CONTROL (4 Fingers Up) ---
        elif isIndexUp and isMiddleUp and isRingUp and isPinkyUp and not isThumbUp:
            screenshot_counter = 0
            mode_text = "HUD: BRIGHTNESS"
            hud_type = "BRIGHTNESS"
            
            bright_dist = math.hypot(x8 - x4, y8 - y4)
            cv2.line(frame, (x4, y4), (x8, y8), (0, 165, 255), 3) 
            
            hud_val = int(np.clip(np.interp(bright_dist, [30, 190], [0, 100]), 0, 100))
            
            if prev_bright_dist != 0:
                if abs(bright_dist - prev_bright_dist) > 5:
                    sbc.set_brightness(hud_val)
                    prev_bright_dist = bright_dist
            else:
                prev_bright_dist = bright_dist
        else:
            screenshot_counter = 0

    # --- Cyberpunk Graphical HUD Layout ---
    # Sleek glassmorphism look for Top Status Banner
    cv2.rectangle(frame, (15, 15), (500, 65), (30, 20, 10), -1) # Semi-dark overlay tint
    cv2.rectangle(frame, (15, 15), (500, 65), (0, 255, 255), 1)  # Tech cyan border
    cv2.putText(frame, mode_text, (30, 48), cv2.FONT_HERSHEY_CR_OUTLINE if False else cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)

    # Floating Audio/Brightness Sidebar Gauge
    if hud_type:
        bar_color = (0, 255, 255) if hud_type == "VOLUME" else (0, 165, 255)
        cv2.rectangle(frame, (45, 150), (70, 400), (20, 20, 20), -1)
        cv2.rectangle(frame, (45, 150), (70, 400), (100, 100, 100), 1)
        
        bar_y = int(np.interp(hud_val, [0, 100], [400, 150]))
        cv2.rectangle(frame, (45, bar_y), (70, 400), bar_color, -1)
        cv2.putText(frame, f"{hud_type}: {hud_val}%", (35, 425), cv2.FONT_HERSHEY_SIMPLEX, 0.5, bar_color, 2)

    # Core System Diagnostics Footer Display
    cTime = time.time()
    fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
    pTime = cTime
    cv2.putText(frame, f"FPS: {int(fps)} | 'f':FullScreen | 'q':Exit", (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

    cv2.imshow('Ultimate Virtual Controller HUD', frame)
    
    # Key checking for Window control hooks
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('f'): # Native full screen toggle switch
        is_fullscreen = not is_fullscreen
        if is_fullscreen:
            cv2.setWindowProperty('Ultimate Virtual Controller HUD', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.setWindowProperty('Ultimate Virtual Controller HUD', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

cap.release()
cv2.destroyAllWindows()