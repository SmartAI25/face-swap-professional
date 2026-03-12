import cv2
import numpy as np
import mediapipe as mp
from PIL import Image
import os
from tqdm import tqdm
import traceback
from datetime import datetime

class FaceSwapEngine:
    def __init__(self):
        """Initialize Face Swap Engine with all features"""
        try:
            self.mp_face_mesh = mp.solutions.face_mesh
            print("✓ MediaPipe Face Mesh loaded")
        except Exception as e:
            print(f"✗ MediaPipe Error: {e}")
            self.mp_face_mesh = None
    
    def get_face_landmarks(self, image):
        """Extract face landmarks from image"""
        if self.mp_face_mesh is None:
            return None
        
        try:
            with self.mp_face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=10,
                min_detection_confidence=0.3
            ) as face_mesh:
                results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                return results.multi_face_landmarks if results.multi_face_landmarks else None
        except Exception as e:
            print(f"✗ Face detection error: {e}")
            return None
    
    def landmarks_to_points(self, landmarks, height, width):
        """Convert landmarks to pixel coordinates"""
        points = []
        for lm in landmarks.landmark:
            x = max(0, min(int(lm.x * width), width - 1))
            y = max(0, min(int(lm.y * height), height - 1))
            points.append([x, y])
        return np.array(points, dtype=np.int32)
    
    def create_face_mask(self, image, points):
        """Create precise face mask"""
        h, w = image.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        
        if len(points) < 3:
            return mask
        
        try:
            hull = cv2.convexHull(points)
            cv2.fillConvexPoly(mask, hull, 255)
            
            # Smooth mask edges
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.GaussianBlur(mask, (31, 31), 0)
        except:
            pass
        
        return mask
    
    def warp_face(self, source_img, source_points, target_points, target_shape):
        """Warp source face to target using Delaunay triangulation"""
        h, w = target_shape[:2]
        
        try:
            source_hull = cv2.convexHull(source_points)
            target_hull = cv2.convexHull(target_points)
            
            # Find affine transformations for each triangle
            rect = cv2.boundingRect(target_hull)
            subdiv = cv2.Subdiv2D(rect)
            
            for pt in target_hull:
                subdiv.insert((float(pt[0][0]), float(pt[0][1])))
            
            triangles = subdiv.getTriangleList()
            warped = np.zeros_like(target_shape)
            
            for triangle in triangles:
                pt1 = (int(triangle[0]), int(triangle[1]))
                pt2 = (int(triangle[2]), int(triangle[3]))
                pt3 = (int(triangle[4]), int(triangle[5]))
                
                try:
                    # Get affine transformation
                    src_tri = np.float32([pt1, pt2, pt3])
                    dst_tri = np.float32([pt1, pt2, pt3])
                    
                    M = cv2.getAffineTransform(src_tri[:3], dst_tri[:3])
                    warped_tri = cv2.warpAffine(source_img, M, (w, h))
                    
                    # Create triangle mask
                    tri_mask = np.zeros((h, w), dtype=np.uint8)
                    cv2.fillConvexPoly(tri_mask, np.int32([pt1, pt2, pt3]), 1)
                    
                    warped = np.where(tri_mask[:,:,np.newaxis], warped_tri, warped)
                except:
                    pass
            
            return warped
        except Exception as e:
            print(f"Warp error: {e}")
            return target_shape
    
    def seamless_blend(self, face, target, mask):
        """Seamless blending using Poisson blending"""
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
                    
                    return cv2.seamlessClone(
                        face.astype(np.uint8),
                        target.astype(np.uint8),
                        dilated_mask,
                        (cx, cy),
                        cv2.NORMAL_CLONE
                    )
        except:
            pass
        
        # Fallback alpha blending
        mask_3ch = np.dstack([mask] * 3)
        return (face * mask_3ch + target * (1 - mask_3ch)).astype(np.uint8)
    
    def swap_faces_image(self, source_path, target_path, output_path):
        """Swap faces in static image"""
        print(f"\n📸 Image Face Swap")
        print(f"  Source: {os.path.basename(source_path)}")
        print(f"  Target: {os.path.basename(target_path)}")
        
        source = cv2.imread(source_path)
        target = cv2.imread(target_path)
        
        if source is None or target is None:
            print("❌ Image load error!")
            return False
        
        source = cv2.resize(source, (640, 480))
        sh, sw = source.shape[:2]
        th, tw = target.shape[:2]
        
        # Get source face
        source_landmarks = self.get_face_landmarks(source)
        if not source_landmarks:
            print("❌ No face found in source!")
            return False
        
        source_points = self.landmarks_to_points(source_landmarks[0], sh, sw)
        
        # Get target faces
        target_landmarks = self.get_face_landmarks(target)
        if not target_landmarks:
            print("❌ No face found in target!")
            return False
        
        result = target.copy()
        
        # Swap each face
        for idx, target_lm in enumerate(target_landmarks):
            print(f"  Swapping face {idx+1}/{len(target_landmarks)}...")
            
            target_points = self.landmarks_to_points(target_lm, th, tw)
            
            # Warp
            warped = self.warp_face(source, source_points, target_points, result)
            
            # Mask
            mask = self.create_face_mask(result, target_points) / 255.0
            
            # Blend
            result = self.seamless_blend(warped, result, mask)
        
        cv2.imwrite(output_path, result)
        print(f"✅ Saved: {output_path}")
        return True
    
    def swap_faces_video(self, source_path, video_path, output_path, max_duration=None, progress_callback=None):
        """Swap faces in video with progress tracking"""
        print(f"\n🎬 Video Face Swap")
        print(f"  Source: {os.path.basename(source_path)}")
        print(f"  Video: {os.path.basename(video_path)}")
        
        source = cv2.imread(source_path)
        if source is None:
            print("❌ Source image error!")
            return False
        
        source = cv2.resize(source, (640, 480))
        sh, sw = source.shape[:2]
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("❌ Video load error!")
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
        print(f"  Total Frames: {total_frames}")
        print(f"  Duration: ~{total_frames/fps:.1f}s")
        
        # Get source landmarks
        source_landmarks = self.get_face_landmarks(source)
        if not source_landmarks:
            print("❌ No face in source!")
            return False
        
        source_points = self.landmarks_to_points(source_landmarks[0], sh, sw)
        
        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
        
        frame_count = 0
        pbar = tqdm(total=total_frames, desc="Processing")
        
        while frame_count < total_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            try:
                target_landmarks = self.get_face_landmarks(frame)
                result = frame.copy()
                
                if target_landmarks:
                    for target_lm in target_landmarks:
                        target_points = self.landmarks_to_points(target_lm, h, w)
                        warped = self.warp_face(source, source_points, target_points, result)
                        mask = self.create_face_mask(result, target_points) / 255.0
                        result = self.seamless_blend(warped, result, mask)
                
                out.write(result)
            except Exception as e:
                out.write(frame)
                print(f"⚠ Frame {frame_count}: {str(e)[:30]}")
            
            frame_count += 1
            pbar.update(1)
            
            if progress_callback:
                progress_callback(frame_count, total_frames)
        
        pbar.close()
        cap.release()
        out.release()
        
        print(f"✅ Saved: {output_path}")
        return True
    
    def generate_video_from_image(self, image_path, output_path, duration=5, fps=24):
        """Generate video from static image (simple version)"""
        print(f"\n🎥 Generating Video from Image")
        print(f"  Image: {os.path.basename(image_path)}")
        print(f"  Duration: {duration}s")
        
        image = cv2.imread(image_path)
        if image is None:
            print("❌ Image load error!")
            return False
        
        h, w = image.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
        
        total_frames = int(fps * duration)
        
        print(f"  Resolution: {w}x{h}")
        print(f"  FPS: {fps}")
        print(f"  Total Frames: {total_frames}")
        
        for i in tqdm(range(total_frames), desc="Generating"):
            # Add subtle zoom/pan effect
            scale = 1 + (0.1 * np.sin(2 * np.pi * i / total_frames))
            h_img, w_img = image.shape[:2]
            center_x, center_y = w_img // 2, h_img // 2
            
            matrix = cv2.getRotationMatrix2D((center_x, center_y), 0, scale)
            frame = cv2.warpAffine(image, matrix, (w_img, h_img))
            
            out.write(frame)
        
        out.release()
        print(f"✅ Video saved: {output_path}")
        return True

# Test
if __name__ == "__main__":
    engine = FaceSwapEngine()
    print("Face Swap Engine Ready!")