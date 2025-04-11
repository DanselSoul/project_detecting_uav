# backend/app/yolo/yolo_model.py

from ultralytics import YOLO
import torch

print("[INFO] Initializing YOLO model...")
model = YOLO("backend/app/yolo/yolo11n_best.pt")

device = "cuda:0" if torch.cuda.is_available() else "cpu"
model.to(device)
print(f"[INFO] YOLO model loaded on device: {device}")
