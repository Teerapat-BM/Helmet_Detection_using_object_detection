from ultralytics import YOLO
import cv2
import numpy as np
from scipy.optimize import linear_sum_assignment
import time
import requests
import json

API_ENDPOINT = "http://localhost:8000/counts/"

# Load the YOLOv8 model
model = YOLO('model/best.pt')  # Replace with your trained model path

# Initialize video capture
cap = cv2.VideoCapture('test/test.mp4') # Change to your video path

if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

# Initialize variables
helmet_count = 0
no_helmet_count = 0
tracked_objects = {}  # Dictionary to store tracked objects and their counting status
next_id = 0

# Function to calculate center of a bounding box
def get_box_center(box):
    return ((box[0] + box[2]) // 2, (box[1] + box[3]) // 2)

# Function to calculate distance between two points
def distance(p1, p2):
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# Warm up the model
dummy_input = np.random.randint(0, 255, (540, 960, 3), dtype=np.uint8)
for _ in range(10):
    model(dummy_input)

frame_count = 0
start_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break
    
    # Resize frame to smaller dimensions for faster processing
    frame = cv2.resize(frame, (960, 540))

    # Perform detection
    results = model(frame, conf=0.5)

    # Current frame's objects
    current_objects = {}

    # Process detection results
    for result in results:
        boxes = result.boxes.xyxy.cpu().numpy()
        confidences = result.boxes.conf.cpu().numpy()
        class_ids = result.boxes.cls.cpu().numpy().astype(int)

        # Prepare cost matrix for Hungarian algorithm
        cost_matrix = np.zeros((len(boxes), len(tracked_objects)))
        for i, box in enumerate(boxes):
            center = get_box_center(box)
            for j, (track_id, tracked_obj) in enumerate(tracked_objects.items()):
                cost_matrix[i, j] = distance(center, tracked_obj['center'])

        # Use Hungarian algorithm for tracking
        if tracked_objects:
            row_ind, col_ind = linear_sum_assignment(cost_matrix)
        else:
            row_ind, col_ind = [], []

        # Process detections
        assigned_tracks = set()
        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = map(int, box)
            confidence = confidences[i]
            class_id = class_ids[i]
            label = model.names[class_id]
            center = get_box_center((x1, y1, x2, y2))

            matched = False
            if i in row_ind:
                j = col_ind[list(row_ind).index(i)]
                if cost_matrix[i, j] < 50:  # Distance threshold
                    track_id = list(tracked_objects.keys())[j]
                    matched = True
                    assigned_tracks.add(track_id)
                    # Update existing track
                    tracked_objects[track_id].update({
                        'center': center,
                        'last_seen': frame_count,
                        'label': label
                    })

            if not matched:
                # Create new track
                track_id = next_id
                next_id += 1
                tracked_objects[track_id] = {
                    'center': center,
                    'label': label,
                    'counted': False,
                    'last_seen': frame_count
                }
                assigned_tracks.add(track_id)
                
                # Count new objects
                if not tracked_objects[track_id]['counted']:
                    if label == "helmet":
                        helmet_count += 1
                    elif label == "no helmet":
                        no_helmet_count += 1
                    tracked_objects[track_id]['counted'] = True

            # Draw bounding box and label
            color = (0, 255, 0) if label == "helmet" else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{label}: {confidence:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Remove old tracks
    tracked_objects = {k: v for k, v in tracked_objects.items() 
                      if frame_count - v['last_seen'] < 100}  # Remove after 30 frames of absence

    # Display counts
    current_helmets = sum(1 for obj in tracked_objects.values() if obj['label'] == "helmet")
    current_no_helmets = sum(1 for obj in tracked_objects.values() if obj['label'] == "no helmet")
    
    cv2.putText(frame, f"Current Helmets: {current_helmets}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.putText(frame, f"Current No Helmets: {current_no_helmets}", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.putText(frame, f"Total Helmets: {helmet_count}", (10, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.putText(frame, f"Total No Helmets: {no_helmet_count}", (10, 150),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    # Display the frame
    cv2.imshow('Real-Time Helmet Detection', frame)

    # Calculate FPS
    frame_count += 1
    if frame_count % 30 == 0:
        end_time = time.time()
        fps = 30 / (end_time - start_time)
        print(f"FPS: {fps:.2f}")
        start_time = time.time()

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # ในลูป while True เพิ่มโค้ดสำหรับส่งข้อมูลไป API ทุกๆ 5 วินาที
    if frame_count % 150 == 0:  # ทุกๆ 5 วินาที (ที่ 30 FPS)
        try:
            data = {
                "helmet_count": helmet_count,
                "no_helmet_count": no_helmet_count
            }
            response = requests.post(API_ENDPOINT, json=data)
            if response.status_code == 200:
                print("Data successfully sent to API")
            else:
                print(f"Failed to send data: {response.status_code}")
        except Exception as e:
            print(f"Error sending data to API: {e}")

# Cleanup
cap.release()
cv2.destroyAllWindows()

print(f"Final Total Helmets detected: {helmet_count}")
print(f"Final Total No Helmets detected: {no_helmet_count}")

