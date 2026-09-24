import cv2

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    ret, frame = camera.read()

    if not ret:
        break

    cv2.imshow("DriveSafe AI - Camera Test", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
