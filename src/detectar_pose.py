from pathlib import Path
import time

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# A partir de src/detectar_pose.py, volta uma pasta até a raiz do projeto.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "pose_landmarker_lite.task"

# Um landmark abaixo desta visibilidade não será desenhado.
VISIBILITY_THRESHOLD = 0.5

# Conexões principais do esqueleto.
# Os números correspondem aos 33 landmarks do MediaPipe.
POSE_CONNECTIONS = (
    (11, 12),                 # ombro esquerdo - ombro direito
    (11, 13), (13, 15),       # braço esquerdo
    (12, 14), (14, 16),       # braço direito
    (11, 23), (12, 24),       # ombros - quadris
    (23, 24),                 # quadril esquerdo - quadril direito
    (23, 25), (25, 27),       # perna esquerda
    (27, 29), (29, 31),
    (27, 31),                 # pé esquerdo
    (24, 26), (26, 28),       # perna direita
    (28, 30), (30, 32),
    (28, 32),                 # pé direito
)


def draw_pose(frame, landmarks):
    """Desenha os landmarks visíveis e as conexões principais."""

    height, width = frame.shape[:2]
    points = []

    for landmark in landmarks:
        visibility = getattr(landmark, "visibility", 1.0)

        if visibility is None:
            visibility = 1.0

        # Converte coordenadas normalizadas [0, 1] para pixels.
        x = int(landmark.x * width)
        y = int(landmark.y * height)

        inside_frame = 0 <= x < width and 0 <= y < height

        if visibility >= VISIBILITY_THRESHOLD and inside_frame:
            points.append((x, y))
        else:
            points.append(None)

    # Desenha primeiro as linhas.
    for start_index, end_index in POSE_CONNECTIONS:
        start = points[start_index]
        end = points[end_index]

        if start is not None and end is not None:
            cv2.line(
                frame,
                start,
                end,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

    # Desenha os 33 pontos visíveis.
    for point in points:
        if point is not None:
            cv2.circle(
                frame,
                point,
                4,
                (0, 0, 255),
                -1,
                cv2.LINE_AA,
            )


def open_camera():
    """Abre a webcam com DirectShow e tenta o backend padrão como reserva."""

    capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not capture.isOpened():
        capture.release()
        capture = cv2.VideoCapture(0)

    return capture


def main():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Modelo não encontrado: {MODEL_PATH}"
        )

    options = vision.PoseLandmarkerOptions(
        base_options=python.BaseOptions(
            model_asset_path=str(MODEL_PATH)
        ),
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    capture = open_camera()

    if not capture.isOpened():
        raise RuntimeError("Não foi possível abrir a webcam.")

    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    previous_time = time.perf_counter()
    smoothed_fps = 0.0
    last_timestamp_ms = -1

    try:
        with vision.PoseLandmarker.create_from_options(options) as landmarker:
            while True:
                success, frame = capture.read()

                if not success or frame is None:
                    print("Falha ao capturar um quadro da webcam.")
                    break

                # O OpenCV trabalha em BGR; o MediaPipe espera RGB.
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                mp_image = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=rgb_frame,
                )

                # No modo VIDEO, cada quadro precisa de um timestamp crescente.
                timestamp_ms = int(time.monotonic() * 1000)
                timestamp_ms = max(
                    timestamp_ms,
                    last_timestamp_ms + 1,
                )
                last_timestamp_ms = timestamp_ms

                result = landmarker.detect_for_video(
                    mp_image,
                    timestamp_ms,
                )

                pose_detected = bool(result.pose_landmarks)

                if pose_detected:
                    draw_pose(
                        frame,
                        result.pose_landmarks[0],
                    )

                # FPS médio suavizado para evitar números muito oscilantes.
                current_time = time.perf_counter()
                elapsed = current_time - previous_time
                previous_time = current_time

                instantaneous_fps = (
                    1.0 / elapsed if elapsed > 0 else 0.0
                )

                if smoothed_fps == 0.0:
                    smoothed_fps = instantaneous_fps
                else:
                    smoothed_fps = (
                        0.9 * smoothed_fps
                        + 0.1 * instantaneous_fps
                    )

                cv2.putText(
                    frame,
                    f"FPS: {smoothed_fps:.1f}",
                    (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                cv2.putText(
                    frame,
                    "Q ou ESC para sair",
                    (15, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                cv2.imshow(
                    "Deteccao de pose - linha de base",
                    frame,
                )

                key = cv2.waitKey(1) & 0xFF

                if key in (ord("q"), ord("Q"), 27):
                    break

    finally:
        # Executado inclusive quando ocorre uma exceção.
        capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
