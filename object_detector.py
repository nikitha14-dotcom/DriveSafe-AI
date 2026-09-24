import cv2
from ultralytics import YOLOWorld

# ============================================================
# LOAD YOLO-WORLD MODEL
# ============================================================

print("Loading YOLO-World model...")

model = YOLOWorld("yolov8s-world.pt")

# ============================================================
# OBJECTS WE WANT TO DETECT
# ============================================================

model.set_classes([
    "mobile phone",
    "smartphone",
    "bluetooth earbuds",
    "wireless earbuds",
    "earphones",
    "USB pen drive",
    "USB flash drive",
    "laptop",
    "bottle",
    "cup",
    "book",
    "person"
])

print("Model loaded successfully.")
print("Starting camera...")

# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open camera.")
    exit()

print("Camera started.")
print("Press Q to quit.")

# ============================================================
# MAIN LOOP
# ============================================================

while True:

    ret, frame = cap.read()

    if not ret:
        print("ERROR: Could not read camera.")
        break

    # Mirror camera
    frame = cv2.flip(frame, 1)

    # ========================================================
    # OBJECT DETECTION
    # ========================================================

    results = model(
        frame,
        verbose=False,
        conf=0.25
    )

    # Draw detections
    annotated_frame = results[0].plot()

    # ========================================================
    # DISPLAY
    # ========================================================

    cv2.imshow(
        "DriveSafe AI - Object Detection",
        annotated_frame
    )

    # ========================================================
    # QUIT
    # ========================================================

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ============================================================
# CLEANUP
# ============================================================

cap.release()
cv2.destroyAllWindows()

print("Camera closed.")