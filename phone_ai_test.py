import cv2
from phone_ai import detect_phone

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera could not be opened.")
    exit()

print("DriveSafe AI - Real Phone Detection")
print("Hold a phone in front of the camera.")
print("Press Q to quit.")

while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)

    detected, confidence = detect_phone(frame)

    if detected:

        cv2.putText(
            frame,
            "PHONE DETECTED",
            (20, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 255),
            3
        )

        cv2.putText(
            frame,
            f"Confidence: {confidence:.2f}",
            (20, 85),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )

    else:

        cv2.putText(
            frame,
            "NO PHONE",
            (20, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0),
            2
        )

    cv2.imshow(
        "DriveSafe AI - Real Phone Detection",
        frame
    )

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

print("Phone detection test completed.")import cv2
from phone_ai import detect_phone

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera could not be opened.")
    exit()

print("DriveSafe AI - Real Phone Detection")
print("Hold a phone in front of the camera.")
print("Press Q to quit.")

while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)

    detected, confidence = detect_phone(frame)

    if detected:

        cv2.putText(
            frame,
            "PHONE DETECTED",
            (20, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 255),
            3
        )

        cv2.putText(
            frame,
            f"Confidence: {confidence:.2f}",
            (20, 85),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )

    else:

        cv2.putText(
            frame,
            "NO PHONE",
            (20, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0),
            2
        )

    cv2.imshow(
        "DriveSafe AI - Real Phone Detection",
        frame
    )

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

print("Phone detection test completed.")