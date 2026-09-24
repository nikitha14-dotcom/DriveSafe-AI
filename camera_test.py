import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Unable to open webcam")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)

    cv2.putText(
        frame,
        "DriveSafe AI Camera Test",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2,
    )

    cv2.imshow("DriveSafe AI", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
