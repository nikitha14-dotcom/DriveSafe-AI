"""Interactive real-camera smoke check for the existing PhoneDetector."""


def main():
    import cv2
    from phone_module import PhoneDetector

    detector = PhoneDetector()
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        raise SystemExit("Camera could not be opened.")
    print("Phone detector smoke check: show a phone; press Q to quit.")
    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)
            result = detector.detect(frame)
            for x1, y1, x2, y2, confidence in result["boxes"]:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"PHONE {confidence:.2f}", (x1, max(20, y1 - 8)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            status = "PHONE DETECTED" if result["detected"] else "NO PHONE DETECTED"
            cv2.putText(frame, status, (20, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (0, 0, 255) if result["detected"] else (0, 255, 0), 2)
            cv2.imshow("DriveSafe AI - Phone Detector Smoke Check", frame)
            if cv2.waitKey(1) & 0xFF in (ord("q"), ord("Q")):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
