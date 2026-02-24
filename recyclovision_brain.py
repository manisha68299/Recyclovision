import cv2
import numpy as np
from ultralytics import YOLO
import pyttsx3
import threading
import time
import csv
import os
from datetime import datetime

print("Loading RecycloVision OS // Stable Analytics + Telemetry Edition...")
model = YOLO('yolov8s.pt') 

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

window_name = 'RecycloVision OS - AMD Powered'
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

WET_WASTE = [46, 47, 48, 49, 50, 51, 52, 53, 54, 55] 
RECYCLABLE = [39, 40, 41, 42, 43, 44, 45, 73, 24, 25, 26, 28, 27, 76, 79]
E_WASTE = [63, 64, 65, 66, 67, 68, 69, 70, 62, 72]
ALLOWED_CLASSES = WET_WASTE + RECYCLABLE + E_WASTE

CURRENT_BIN_NAME = "RECYCLING"
CURRENT_VALID_LIST = RECYCLABLE

# --- ROCK-SOLID ANALYTICS ---
correct_count = 0
wrong_count = 0
last_action_time = 0
ACTION_COOLDOWN = 4.0 # Locks the counter and voice for 4 seconds after an item is scanned

# --- INITIALIZE CSV TELEMETRY DATABASE ---
CSV_FILE = "waste_telemetry.csv"
file_exists = os.path.isfile(CSV_FILE)

with open(CSV_FILE, mode='a', newline='') as file:
    writer = csv.writer(file)
    if not file_exists:
        # Create headers if the file is brand new
        writer.writerow(["Timestamp", "Object_Detected", "Confidence_Score", "Target_Bin", "Status"])

def speak_alert(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 160) 
    engine.say(text)
    engine.runAndWait()

def draw_hud_box(frame, x1, y1, x2, y2, color):
    length = 25
    thickness = 2
    cv2.line(frame, (x1, y1), (x1 + length, y1), color, thickness)
    cv2.line(frame, (x1, y1), (x1, y1 + length), color, thickness)
    cv2.line(frame, (x2, y1), (x2 - length, y1), color, thickness)
    cv2.line(frame, (x2, y1), (x2, y1 + length), color, thickness)
    cv2.line(frame, (x1, y2), (x1 + length, y2), color, thickness)
    cv2.line(frame, (x1, y2), (x1, y2 - length), color, thickness)
    cv2.line(frame, (x2, y2), (x2 - length, y2), color, thickness)
    cv2.line(frame, (x2, y2), (x2, y2 - length), color, thickness)

prev_time = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
        
    h, w = frame.shape[:2]
    current_time = time.time()
    
    fps = 1 / (current_time - prev_time) if (current_time - prev_time) > 0 else 0
    prev_time = current_time
    latency_ms = int((1 / fps) * 1000) if fps > 0 else 0
        
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 100), (12, 12, 12), -1)
    cv2.addWeighted(overlay, 0.9, frame, 0.1, 0, frame)
    
    # Left Column
    cv2.putText(frame, "RECYCLOVISION // SYSTEM ACTIVE", (30, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 1)
    cv2.putText(frame, f"MODE: {CURRENT_BIN_NAME} BIN (Keys: 1, 2, 3)", (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 200, 200), 2)
    
    # Center Column (Live Counters)
    center_x = int(w / 2) - 100
    cv2.putText(frame, f"CORRECT DISPOSALS: {correct_count}", (center_x, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (50, 255, 100), 2)
    cv2.putText(frame, f"CONTAMINATIONS BLOCKED: {wrong_count}", (center_x, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (50, 50, 255), 2)
    
    # Right Column
    right_x = w - 420
    cv2.putText(frame, "PLATFORM: AMD KRIA KV260 VISION AI", (right_x, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 140, 255), 1)
    cv2.putText(frame, f"VITIS AI ENGINE // {fps:.1f} FPS", (right_x, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 140, 255), 1)
    cv2.putText(frame, f"EDGE LATENCY: {latency_ms} ms", (right_x, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 140, 255), 1)

    results = model(frame, conf=0.60, classes=ALLOWED_CLASSES)
    
    # Process detections
    if len(results) > 0 and len(results[0].boxes) > 0:
        boxes = results[0].boxes
        
        # Draw visual UI for ALL detected items in frame
        for box in boxes:
            class_id = int(box.cls[0])
            object_name = model.names[class_id].upper()
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            if class_id in CURRENT_VALID_LIST:
                color = (50, 255, 100) 
                status = "CORRECT"
            else:
                color = (50, 50, 255) 
                status = "WARNING"
            
            draw_hud_box(frame, x1, y1, x2, y2, color)
            
            label_bg_y1 = y1 - 35
            label_bg_y2 = y1
            text_y = y1 - 10
            
            if y1 < 120: 
                label_bg_y1 = y2
                label_bg_y2 = y2 + 35
                text_y = y2 + 25
                
            cv2.rectangle(frame, (x1, label_bg_y1), (x1 + 250, label_bg_y2), color, -1)
            cv2.putText(frame, f"{status} | {object_name}", (x1 + 10, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (10, 10, 10), 2)

        # ---------------------------------------------------------
        # THE FIX + DATA TELEMETRY LOGGING
        # ---------------------------------------------------------
        if current_time - last_action_time > ACTION_COOLDOWN:
            # YOLO naturally sorts boxes by highest confidence first
            primary_box = boxes[0] 
            primary_id = int(primary_box.cls[0])
            primary_name = model.names[primary_id].upper()
            
            # Get data for CSV
            confidence_score = float(primary_box.conf[0])
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if primary_id in CURRENT_VALID_LIST:
                correct_count += 1
                msg = f"{primary_name} accepted."
                log_status = "CORRECT"
            else:
                wrong_count += 1
                msg = f"Warning. {primary_name} does not belong in {CURRENT_BIN_NAME}."
                log_status = "CONTAMINATION_PREVENTED"
                
            # --- WRITE TO CSV ---
            with open(CSV_FILE, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, primary_name, f"{confidence_score:.2f}", CURRENT_BIN_NAME, log_status])
            
            # Trigger voice on background thread
            t = threading.Thread(target=speak_alert, args=(msg,))
            t.start()
            
            # Lock the system from counting again for 4 seconds
            last_action_time = current_time

    cv2.imshow(window_name, frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('1'):
        CURRENT_BIN_NAME = "RECYCLING"
        CURRENT_VALID_LIST = RECYCLABLE
    elif key == ord('2'):
        CURRENT_BIN_NAME = "WET WASTE"
        CURRENT_VALID_LIST = WET_WASTE
    elif key == ord('3'):
        CURRENT_BIN_NAME = "E-WASTE"
        CURRENT_VALID_LIST = E_WASTE

cap.release()
cv2.destroyAllWindows()