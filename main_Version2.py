import cv2
import numpy as np
import mediapipe as mp
from tqdm import tqdm
import os
from datetime import datetime

class FaceSwapEngine:
    def __init__(self):
        try:
            self.mp_face_mesh = mp.solutions.face_mesh
            print("✓ Engine Ready")
        except:
            print("✗ MediaPipe error - reinstalling...")
            os.system("pip install --upgrade mediapipe")
            self.mp_face_mesh = mp.solutions.face_mesh
    
    def get_face_landmarks(self, image):
        if self.mp_face_mesh is None:
            return None
        try:
            with self.mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=10) as face_mesh:
                results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                return results.multi_face_landmarks if results.multi_face_landmarks else None
        except:
            return None
    
    def landmarks_to_points(self, landmarks, height, width):
        points = []
        for lm in landmarks.landmark:
            x = max(0, min(int(lm.x * width), width - 1))
            y = max(0, min(int(lm.y * height), height - 1))
            points.append([x, y])
        return np.array(points, dtype=np.int32)
    
    def create_face_mask(self, image, points):
        h, w = image.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        if len(points) < 3:
            return mask
        try:
            hull = cv2.convexHull(points)
            cv2.fillConvexPoly(mask, hull, 255)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.GaussianBlur(mask, (31, 31), 0)
        except:
            pass
        return mask
    
    def seamless_blend(self, face, target, mask):
        try:
            mask_uint8 = (mask * 255).astype(np.uint8)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
            dilated_mask = cv2.dilate(mask_uint8, kernel, iterations=2)
            contours, _ = cv2.findContours(dilated_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest = max(contours, key=cv2.contourArea)
                M = cv2.moments(largest)
                if M["m00"] > 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    return cv2.seamlessClone(face.astype(np.uint8), target.astype(np.uint8), dilated_mask, (cx, cy), cv2.NORMAL_CLONE)
        except:
            pass
        mask_3ch = np.dstack([mask] * 3)
        return (face * mask_3ch + target * (1 - mask_3ch)).astype(np.uint8)
    
    def swap_faces_image(self, source_path, target_path, output_path):
        print(f"\n📸 Image Face Swap")
        print(f"  Source: {os.path.basename(source_path)}")
        print(f"  Target: {os.path.basename(target_path)}")
        
        source = cv2.imread(source_path)
        target = cv2.imread(target_path)
        
        if source is None or target is None:
            print("❌ Error loading images!")
            return False
        
        source = cv2.resize(source, (640, 480))
        sh, sw = source.shape[:2]
        th, tw = target.shape[:2]
        
        source_landmarks = self.get_face_landmarks(source)
        if not source_landmarks:
            print("❌ No face in source!")
            return False
        
        source_points = self.landmarks_to_points(source_landmarks[0], sh, sw)
        
        target_landmarks = self.get_face_landmarks(target)
        if not target_landmarks:
            print("❌ No face in target!")
            return False
        
        result = target.copy()
        
        for idx, target_lm in enumerate(target_landmarks):
            print(f"  Swapping face {idx+1}/{len(target_landmarks)}...")
            target_points = self.landmarks_to_points(target_lm, th, tw)
            target_hull = cv2.convexHull(target_points)
            
            try:
                M = cv2.getAffineTransform(np.float32(cv2.convexHull(source_points)[:3]), np.float32(target_hull[:3]))
                warped = cv2.warpAffine(source, M, (tw, th))
                mask = self.create_face_mask(result, target_points) / 255.0
                result = self.seamless_blend(warped, result, mask)
            except:
                pass
        
        cv2.imwrite(output_path, result)
        print(f"✅ Saved: {output_path}")
        return True
    
    def swap_faces_video(self, source_path, video_path, output_path, max_duration=None):
        print(f"\n🎬 Video Face Swap")
        print(f"  Source: {os.path.basename(source_path)}")
        print(f"  Video: {os.path.basename(video_path)}")
        
        source = cv2.imread(source_path)
        if source is None:
            print("❌ Source error!")
            return False
        
        source = cv2.resize(source, (640, 480))
        sh, sw = source.shape[:2]
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("❌ Video error!")
            return False
        
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if max_duration:
            max_frames = int(fps * max_duration * 60)
            total_frames = min(total_frames, max_frames)
        
        print(f"  Resolution: {w}x{h}")
        print(f"  FPS: {fps}")
        print(f"  Frames: {total_frames}")
        
        source_landmarks = self.get_face_landmarks(source)
        if not source_landmarks:
            print("❌ No face in source!")
            return False
        
        source_points = self.landmarks_to_points(source_landmarks[0], sh, sw)
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
        
        frame_count = 0
        for _ in tqdm(range(total_frames), desc="Processing"):
            ret, frame = cap.read()
            if not ret:
                break
            
            try:
                target_landmarks = self.get_face_landmarks(frame)
                result = frame.copy()
                
                if target_landmarks:
                    for target_lm in target_landmarks:
                        target_points = self.landmarks_to_points(target_lm, h, w)
                        target_hull = cv2.convexHull(target_points)
                        try:
                            M = cv2.getAffineTransform(np.float32(cv2.convexHull(source_points)[:3]), np.float32(target_hull[:3]))
                            warped = cv2.warpAffine(source, M, (w, h))
                            mask = self.create_face_mask(result, target_points) / 255.0
                            result = self.seamless_blend(warped, result, mask)
                        except:
                            pass
                
                out.write(result)
            except:
                out.write(frame)
            
            frame_count += 1
        
        cap.release()
        out.release()
        print(f"✅ Saved: {output_path}")
        return True
    
    def generate_video_from_image(self, image_path, output_path, duration=5, fps=24):
        print(f"\n🎥 Generating Video from Image")
        print(f"  Duration: {duration}s @ {fps}fps")
        
        image = cv2.imread(image_path)
        if image is None:
            print("❌ Error!")
            return False
        
        h, w = image.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
        
        total_frames = int(fps * duration)
        
        for i in tqdm(range(total_frames), desc="Generating"):
            scale = 1 + (0.1 * np.sin(2 * np.pi * i / total_frames))
            center_x, center_y = w // 2, h // 2
            matrix = cv2.getRotationMatrix2D((center_x, center_y), 0, scale)
            frame = cv2.warpAffine(image, matrix, (w, h))
            out.write(frame)
        
        out.release()
        print(f"✅ Saved: {output_path}")
        return True

if __name__ == "__main__":
    engine = FaceSwapEngine()
    
    print("\n" + "="*50)
    print("🎭 FACE SWAP PROFESSIONAL")
    print("="*50)
    print("\n1. Image Swap\n2. Video Swap\n3. Image to Video")
    choice = input("\nChoose (1/2/3): ").strip()
    
    if choice == "1":
        source = input("Source image: ").strip() or "face.jpg"
        target = input("Target image: ").strip() or "target.jpg"
        output = input("Output: ").strip() or "output.jpg"
        if os.path.exists(source) and os.path.exists(target):
            engine.swap_faces_image(source, target, output)
        else:
            print("Files not found!")
    
    elif choice == "2":
        source = input("Source image: ").strip() or "face.jpg"
        target = input("Target video: ").strip() or "video.mp4"
        output = input("Output: ").strip() or "output.mp4"
        duration = input("Duration (min): ").strip() or "5"
        if os.path.exists(source) and os.path.exists(target):
            engine.swap_faces_video(source, target, output, max_duration=int(duration))
        else:
            print("Files not found!")
    
    elif choice == "3":
        source = input("Source image: ").strip() or "face.jpg"
        output = input("Output: ").strip() or "output.mp4"
        duration = input("Duration (sec): ").strip() or "5"
        fps = input("FPS: ").strip() or "24"
        if os.path.exists(source):
            engine.generate_video_from_image(source, output, duration=int(duration), fps=int(fps))
        else:
            print("File not found!")
    
    else:
        print("Invalid choice!")