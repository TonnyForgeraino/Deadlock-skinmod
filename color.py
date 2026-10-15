
import time

import cv2
import mss
import numpy as np


WINDOW_NAME = "Live Screen Color Filter"
CAPTURE_SCALE = 0.65
TARGET_FPS = 30
INITIAL_HUE_SHIFT = 90
SATURATION_BOOST = 1.0
VALUE_BOOST = 1.0


def transform_colors(frame, hue_shift):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)

    hsv[:, :, 0] = (hsv[:, :, 0] + hue_shift) % 180
    hsv[:, :, 1] = np.clip(
        hsv[:, :, 1] * SATURATION_BOOST, 0, 255
    )
    hsv[:, :, 2] = np.clip(
        hsv[:, :, 2] * VALUE_BOOST, 0, 255
    )

    result = cv2.cvtColor(
        hsv.astype(np.uint8), cv2.COLOR_HSV2BGR
    )

    return result


def main():
    hue_shift = INITIAL_HUE_SHIFT
    frame_duration = 1.0 / TARGET_FPS

    with mss.mss() as screen:
        monitor = screen.monitors[1]

        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

        while True:
            start = time.perf_counter()

            screenshot = np.array(screen.grab(monitor))
            frame = cv2.cvtColor(
                screenshot, cv2.COLOR_BGRA2BGR
            )

            if CAPTURE_SCALE != 1.0:
                frame = cv2.resize(
                    frame,
                    None,
                    fx=CAPTURE_SCALE,
                    fy=CAPTURE_SCALE,
                    interpolation=cv2.INTER_AREA,
                )

            filtered = transform_colors(frame, hue_shift)

            cv2.putText(
                filtered,
                f"Hue shift: {hue_shift} | Q: quit | "
                f"A/D: adjust | R: reset",
                (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow(WINDOW_NAME, filtered)

            key = cv2.waitKey(1) & 0xFF

            if key in (ord("q"), 27):
                break
            elif key == ord("a"):
                hue_shift = (hue_shift - 5) % 180
            elif key == ord("d"):
                hue_shift = (hue_shift + 5) % 180
            elif key == ord("r"):
                hue_shift = INITIAL_HUE_SHIFT

            elapsed = time.perf_counter() - start
            remaining = frame_duration - elapsed

            if remaining > 0:
                time.sleep(remaining)

        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
