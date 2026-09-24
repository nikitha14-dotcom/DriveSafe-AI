import cv2
import time
from phone_detector import PhoneDetector


class LiveDetection:

    def __init__(self):
        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            print("Camera could not be opened.")
            return

        print("Camera started.")
        print("Starting phone detection...")
        print("Press Q to quit.")

        self.phone_detector = PhoneDetector()

    def run(self):

        while True:

            ret, frame = self.cap.read()

            if not ret:
                print("Camera frame could not be read.")
                break

            phone_detected = False

            try:
                result = self.phone_detector.detect(frame)

                if result:
                    phone_detected = True

            except Exception:
                phone_detected = False

            cv2.putText(
                frame,
                "DriveSafe AI",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                "Camera: ACTIVE",
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            if phone_detected:
                cv2.putText(
                    frame,
                    "PHONE DETECTED",
                    (20, 115),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2
                )
            else:
                cv2.putText(
                    frame,
                    "PHONE: NOT DETECTED",
                    (20, 115),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

            cv2.imshow("DriveSafe AI - Live Detection", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

        self.cap.release()
        cv2.destroyAllWindows()

        print("Live detection stopped.")


if __name__ == "__main__":

    app = LiveDetection()
    app.run()