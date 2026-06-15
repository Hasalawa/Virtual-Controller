# 🦾 CyberHUD: Ultimate Virtual System Controller

An advanced, next-level computer vision application that transforms your hand into a powerful universal remote for your PC. Built with **OpenCV** and **Google MediaPipe**, it features a sleek, cyberpunk-inspired Holographic HUD and allows you to control your mouse, system volume, screen brightness, and media playback entirely through natural hand gestures.

## ✨ Next-Level Features

* 🎛️ **Cyberpunk HUD:** A highly stylized, glassmorphism-inspired UI with glowing tracking boundaries, live telemetry, and dynamic level bars.
* 🖱️ **Velocity-Based Dynamic Mouse:** The mouse pointer adapts to your hand speed. Move fast for quick navigation, or move slow for ultra-precise, jitter-free clicking.
* 🔊 **Fluid Audio & Brightness Control:** Adjust system volume and screen brightness smoothly by measuring the precise distance between your fingers.
* 📸 **Smart System Capture:** Take full-screen screenshots simply by holding your hand open for 1.5 seconds.
* 🎵 **Media Control:** Play or pause your music/videos instantly with a simple hand sign.
* 🪟 **Advanced OS Macros:** Quickly show your desktop or switch between applications using intuitive gesture macros.

## 🛠️ Tech Stack

* **Python 3.x**
* **OpenCV** (`opencv-python`) - Image processing & HUD rendering
* **Google MediaPipe** (`mediapipe`) - Real-time hand landmark tracking
* **PyAutoGUI** (`pyautogui`) - Mouse & keyboard automation
* **Screen Brightness Control** (`screen-brightness-control`) - Display management
* **CTypes** - Native Windows API integration for seamless volume control

## 🚀 Installation & Setup

1. **Clone or Download the Repository:**
   Extract the project files into your desired folder.

2. **Install Required Dependencies:**
   Open your terminal or command prompt and run:
   ```bash
   pip install opencv-python mediapipe numpy pyautogui screen-brightness-control

3. **Download the MediaPipe Model:**
Download the `hand_landmarker.task` file from the [MediaPipe Developer site](https://www.google.com/search?q=https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task) and place it in the same directory as the Python script.
4. **Run the Application:**
```bash
python index.py

```


## ✋ Gesture Guide (How to Use)

### Primary Modes (Fingers Pointing UP)

* ☝️ **1 Finger (Index):** **Mouse Move Mode.** Move your hand to control the cursor. Pinch your thumb and index finger to **Left Click**.
* ✌️ **2 Fingers (Index & Middle):** **Scroll Mode.** Move your hand up/down to scroll web pages. Pinch your thumb and middle finger to **Right Click**.
* 🤟 **3 Fingers (Index, Middle, Ring):** **Master Volume Mode.** Move your thumb and index finger apart/together to increase/decrease the system volume.
* 🖖 **4 Fingers (Index, Middle, Ring, Pinky):** **Screen Brightness Mode.** Move your thumb and index finger apart/together to adjust the monitor's brightness.

### Advanced Macros (Special Signs)

* ✊ **Fist (All fingers closed):** Show Desktop (`Win + D`).
* 🤘 **Rock On (Index & Pinky up):** Application Switcher (`Alt + Tab`).
* 🤙 **Phone Sign (Thumb & Pinky up):** Play / Pause Media.
* 🖐️ **All 5 Fingers Open:** Hold steady for 1.5 seconds to trigger a **Screenshot**. (Images are saved automatically to the project folder).

## ⌨️ Keyboard Shortcuts

* `f` : Toggle Fullscreen HUD Mode
* `q` : Safely Quit the application

---

*Developed with Python, MediaPipe & ❤️*