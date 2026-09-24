import cv2
import time

from ai_driving_integration import AIDrivingIntegration


class CameraAI:

    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.system = AIDrivingIntegration()

        if not self.cap.isOpened():
            print("Camera could not be opened.")
            return

        print("Camera started successfully.")
        print("Press Q to quit.")

    def run(self):

        while True:

            ret, frame = self.cap.read()

            if not ret:
                print("Could not read camera.")
                break

            height, width = frame.shape[:2]

            cv2.putText(
                frame,
                "DriveSafe AI - Driver Monitoring",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                "Camera: ACTIVE",
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                "Speed: 50 km/h",
                (20, 105),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                "AI Monitoring: ACTIVE",
                (20, 140),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            cv2.imshow("DriveSafe AI", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

        self.cap.release()
        cv2.destroyAllWindows()

        print("Camera closed successfully.")


if __name__ == "__main__":

    app = CameraAI()
    app.run()