🖐️ Minecraft Gesture Control with MediaPipe
Control Minecraft using hand gestures with a webcam and computer vision — no keyboard or mouse needed.

🔍 Overview
This project uses MediaPipe for real-time hand tracking and maps specific hand gestures to in-game actions like:

Walking forward

Jumping

Breaking and placing blocks

Opening inventory

Looking around using hand movement

💡 How It Works
The program detects your hand via webcam and recognizes gestures like:

Gesture	Action in Minecraft
Fist	Hold left click (break block)
Open palm	Right click (place block)
Index finger only	Jump
Index + middle up	Walk forward
Pinky only	Left click (pickup)
Thumbs down	Open inventory
Hand movement	Controls camera view

Mouse movement is smoothed using a simple exponential filter for better experience.

📦 Requirements
Python 3.7+

Libraries:

bash
Copy
Edit
pip install opencv-python mediapipe pynput pyautogui
🧠 Tech Stack
MediaPipe – Hand tracking

OpenCV – Webcam input and visualization

PyAutoGUI & Pynput – Keyboard/mouse control

ctypes – Low-level input simulation for better in-game control

▶️ Usage
Launch Minecraft and go to a world.

Run the script:

bash
Copy
Edit
python app.py
Make sure your webcam is on, and keep your hand visible on screen.

Note: Some games (like Minecraft Java) may require running as admin for full input support.

📌 Notes
Works best with good lighting and a clean background.

Smooth mouse camera movement uses the index finger position.

👤 Author
Created by Marwan Mostafa
