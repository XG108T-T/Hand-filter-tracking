
---

## 📄 英文版 README（`README(EN).md`）

```markdown
# 🖐️ Finger Magic - Real-time Hand Filter Effects

A real-time hand interaction effects tool based on MediaPipe and OpenCV. Use both hands to form quadrilaterals, and dynamic filters are applied inside the frame automatically.

## 📄 License
This project is licensed under **CC BY-NC 4.0 (Creative Commons Attribution-NonCommercial 4.0 International)**. You are free to modify and create, but commercial use is prohibited, and it must not be used for any illegal purposes.

## ✨ Features
- Real-time hand tracking (MediaPipe)
- 2-5 fingers freely switchable
- Multiple filter styles (Comic, Invert, Pixel, Thermal)
- Dynamic effect combinations (Glitch, Data Stream, Memory Leak, etc.)
- Simple / Rich mode toggle
- Black & white inversion
- Effects strictly inside the hand-drawn frame, no background occlusion

## 🎮 Shortcuts
- `2-5`: Select number of fingers
- `Q/W/E/R`: Switch global style
- `1`: Toggle Simple / Rich mode
- `Space`: Black & white inversion
- `ESC`: Exit

## 📦 Dependencies
- Python 3.8+
- OpenCV
- MediaPipe
- NumPy

## 🚀 Quick Start (Beginner Guide)

### Step 1: Install Python (if not already)
This program requires Python. If you don't have it:

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download Python 3.8 or higher (choose the version for your system)
3. Run the installer and **make sure to check "Add Python to PATH"**
4. Complete the installation

> 💡 **Verify installation**: Open a command prompt (CMD) or terminal, type `python --version`. If it shows the version number, it's installed.

### Step 2: One-click install dependencies
- **Windows users**: Double-click `setup.bat`
- **Mac/Linux users**: Open a terminal, navigate to the project folder, and run `bash setup.sh`

The script will automatically install all required Python libraries.

### Step 3: Run the program
In the command prompt or terminal, navigate to the project folder and run:
```bash
python FingerMagic_vx.py