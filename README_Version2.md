# 🎭 Face Swap Professional

**Complete, All-In-One Face Swapping & Video Generation Suite**

## ✨ Features

✅ **Image Face Swap** - Swap faces between two images  
✅ **Video Face Swap** - Swap faces in videos (no duration limit!)  
✅ **Image to Video** - Generate videos from static images  
✅ **Multi-Face Support** - Swap multiple faces at once  
✅ **100% Local Processing** - Zero data leaves your machine  
✅ **Professional GUI** - Easy-to-use interface  
✅ **Real-Time Progress** - Track processing status  
✅ **High Quality Output** - 4K support  

## 📋 Requirements

- Python 3.8+
- 4GB+ RAM
- 500MB disk space

## 🚀 Installation

### Windows
```bash
setup.bat
```

### Linux/Mac
```bash
pip install -r requirements.txt
```

## 💻 Usage

```bash
python gui_professional.py
```

## 🎯 Features Explained

### Image Face Swap
```
1. Select source image (face to swap)
2. Select target image
3. Click START
4. Output saved as output_image.jpg
```

### Video Face Swap
```
1. Select source image
2. Select target video
3. Set duration (5-20 minutes)
4. Click START
5. Output saved as output_video.mp4
```

### Image to Video
```
1. Select source image
2. Set duration & FPS
3. Click START
4. Generate video from image
5. Output saved as output_generated.mp4
```

## 📊 Supported Formats

**Images:** JPG, PNG, BMP  
**Videos:** MP4, AVI, MOV (unlimited duration)

## 🔐 Privacy

✓ No internet required  
✓ No account needed  
✓ All data stays local  
✓ No uploads to cloud  
✓ Open source code  

## ⚙️ Advanced Usage

```python
from main_engine import FaceSwapEngine

engine = FaceSwapEngine()

# Image swap
engine.swap_faces_image("source.jpg", "target.jpg", "output.jpg")

# Video swap (5 minutes)
engine.swap_faces_video("source.jpg", "video.mp4", "output.mp4", max_duration=5)

# Generate video from image
engine.generate_video_from_image("image.jpg", "output.mp4", duration=10, fps=24)
```

## 🆘 Troubleshooting

### "Face not detected"
- Use better lighting
- Try different images
- Ensure face is clearly visible

### Slow processing
- Close other applications
- Reduce video resolution
- Use shorter duration

### MediaPipe error
```bash
pip uninstall mediapipe -y
pip install mediapipe==0.10.8
```

## 📝 License

MIT - Free to use and modify

## 🤝 Contributing

Feel free to fork and improve!

---

**Made with ❤️ by SmartAI25**