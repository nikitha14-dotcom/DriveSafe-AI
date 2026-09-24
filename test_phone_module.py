import cv2
from phone_module import PhoneDetector

print("==============================================")
print("DriveSafe AI - PHONE MODULE TEST")
print("==============================================")

detector = PhoneDetector()

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Camera could not start.")
    exit()

print("Camera started.")
print("Phone detection is ACTIVE.")
print("Press Q to quit.")

while True:
    ret, frame = cap.read()

    if not ret:
        print("ERROR: Could not read camera frame.")
        break

    frame = cv2.flip(frame, 1)

    result = detector.detect(frame)

    for x1, y1, x2, y2, confidence in result["boxes"]:
        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"PHONE {confidence:.2f}",
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    status = "PHONE DETECTED" if result["detected"] else "NO PHONE"

    cv2.putText(
        frame,
        status,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 255) if result["detected"] else (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Confidence: {result['confidence']:.2f}",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.imshow("DriveSafe AI - Phone Module Test", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

print("==============================================")
print("Phone module test completed.")
print("Camera closed.")
print("==============================================")