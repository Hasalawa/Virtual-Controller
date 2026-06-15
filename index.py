import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import time
import math
import pyautogui
import ctypes

# Disable PyAutoGUI fail-safe
pyautogui.FAILSAFE = False

# Get screen dimensions
wScr, hScr = pyautogui.size()

# Camera reduction box for mouse mapping
frameR = 120 
smoothening = 6 
plocX, plocY = 0, 0
clocX, clocY = 0, 0
prev_scroll_y = 0
prev_vol_dist = 0

# --- Native Windows Audio Control Setup ---
# Virtual Key codes for Media Control
VK_VOLUME_UP = 0xAF
VK_VOLUME_DOWN = 0xAE

def control_system_volume(action, steps=1):
    """Directly controls Windows volume without third-party libraries"""
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

while True:
    ret, frame = cap.read()
    if not ret: break
    
    frame = cv2.flip(frame, 1) # Mirror effect
    h, w, c = frame.shape
    
    # Draw mapping box
    cv2.rectangle(frame, (frameR, frameR), (w - frameR, h - frameR), (255, 0, 255), 2)

    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mpImage = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgbImage)
    result = detector.detect(mpImage)

    mode_text = "MODE: IDLE"
    vol_bar_y = 400
    vol_per = 0

    if result.hand_landmarks:
        landmarks = result.hand_landmarks[0]
        
        x4, y4 = int(landmarks[4].x * w), int(landmarks[4].y * h)     # Thumb
        x8, y8 = int(landmarks[8].x * w), int(landmarks[8].y * h)     # Index
        x12, y12 = int(landmarks[12].x * w), int(landmarks[12].y * h) # Middle
        x16, y16 = int(landmarks[16].x * w), int(landmarks[16].y * h) # Ring

        isIndexUp = landmarks[8].y < landmarks[6].y 
        isMiddleUp = landmarks[12].y < landmarks[10].y
        isRingUp = landmarks[16].y < landmarks[14].y

        # --- MODE 1: MOUSE MOVE & LEFT CLICK ---
        if isIndexUp and not isMiddleUp and not isRingUp:
            mode_text = "MODE: MOUSE MOVE"
            
            xScr = np.interp(x8, (frameR, w - frameR), (0, wScr))
            yScr = np.interp(y8, (frameR, h - frameR), (0, hScr))
            
            clocX = plocX + (xScr - plocX) / smoothening
            clocY = plocY + (yScr - plocY) / smoothening
            
            pyautogui.moveTo(clocX, clocY)
            plocX, plocY = clocX, clocY
            
            # Left Click Visuals & Action
            left_click_dist = math.hypot(x8 - x4, y8 - y4)
            
            # Draw line between Thumb and Index
            cv2.line(frame, (x4, y4), (x8, y8), (255, 0, 255), 3)
            cx, cy = (x4 + x8) // 2, (y4 + y8) // 2
            cv2.circle(frame, (cx, cy), 8, (255, 0, 255), -1)

            if left_click_dist < 30:
                mode_text = "MODE: LEFT CLICK"
                cv2.circle(frame, (cx, cy), 12, (0, 255, 0), -1) # Green indicates click
                pyautogui.click()
                time.sleep(0.2)

        # --- MODE 2: SCROLLING & RIGHT CLICK ---
        elif isIndexUp and isMiddleUp and not isRingUp:
            fingers_dist = math.hypot(x12 - x8, y12 - y8)
            
            if fingers_dist < 45: # Scrolling
                mode_text = "MODE: SCROLLING"
                if prev_scroll_y != 0:
                    if prev_scroll_y - y8 > 15: pyautogui.scroll(150)
                    elif y8 - prev_scroll_y > 15: pyautogui.scroll(-150)
                prev_scroll_y = y8
                cv2.circle(frame, (x8, y8), 10, (255, 255, 0), -1)
                cv2.circle(frame, (x12, y12), 10, (255, 255, 0), -1)
            else: # Right Click
                prev_scroll_y = 0 
                mode_text = "MODE: READY (RIGHT CLICK)"
                right_click_dist = math.hypot(x12 - x4, y12 - y4)
                
                # Visuals for Right Click
                cv2.line(frame, (x4, y4), (x12, y12), (255, 0, 0), 3)
                
                if right_click_dist < 30:
                    mode_text = "MODE: RIGHT CLICK"
                    cv2.circle(frame, (x12, y12), 15, (0, 255, 255), -1)
                    pyautogui.click(button='right')
                    time.sleep(0.3)

        # --- MODE 3: FLUID VOLUME CONTROL ---
        elif isIndexUp and isMiddleUp and isRingUp:
            mode_text = "MODE: MASTER VOLUME"
            
            vol_dist = math.hypot(x8 - x4, y8 - y4)
            
            # Visual Feedback
            cv2.line(frame, (x4, y4), (x8, y8), (0, 255, 255), 3)
            cx, cy = (x4 + x8) // 2, (y4 + y8) // 2
            cv2.circle(frame, (cx, cy), 10, (0, 255, 255), -1)

            # Map distance for UI Bar
            vol_bar_y = np.interp(vol_dist, [30, 200], [400, 150])
            vol_per = np.interp(vol_dist, [30, 200], [0, 100])

            # Dynamically control system volume based on finger movement
            if prev_vol_dist != 0:
                diff = vol_dist - prev_vol_dist
                # Trigger volume change if fingers move significantly
                if diff > 8: # Fingers moving apart (Volume UP)
                    steps = int(diff / 8)
                    control_system_volume("up", steps)
                    prev_vol_dist = vol_dist
                elif diff < -8: # Fingers moving closer (Volume DOWN)
                    steps = int(abs(diff) / 8)
                    control_system_volume("down", steps)
                    prev_vol_dist = vol_dist
            else:
                prev_vol_dist = vol_dist

            # Red indicator if hands are very close (Muted look)
            if vol_dist < 30:
                cv2.circle(frame, (cx, cy), 12, (0, 0, 255), -1) 

        else:
            prev_scroll_y = 0
            prev_vol_dist = 0

    # --- Draw UI Elements ---
    
    # Top Status Bar
    cv2.rectangle(frame, (10, 10), (450, 60), (0, 0, 0), -1)
    cv2.putText(frame, mode_text, (20, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Volume Bar UI (Only visual representation based on finger distance)
    cv2.rectangle(frame, (50, 150), (85, 400), (200, 200, 200), 3)
    cv2.rectangle(frame, (50, int(vol_bar_y)), (85, 400), (0, 255, 255), -1)
    cv2.putText(frame, f"{int(vol_per)}%", (40, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # FPS Calculation
    cTime = time.time()
    fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
    pTime = cTime
    cv2.putText(frame, f"FPS: {int(fps)}", (w - 120, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow("Advanced Virtual Controller", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()