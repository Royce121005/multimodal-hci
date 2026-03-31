import cv2
import mediapipe as mp
import pyautogui
import time

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=1,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.8
)

SCREEN_W, SCREEN_H = pyautogui.size()
SMOOTH = 0.2
prev_mx, prev_my = SCREEN_W // 2, SCREEN_H // 2

def smooth_cursor(mx, my):
    global prev_mx, prev_my
    prev_mx = int(prev_mx + SMOOTH * (mx - prev_mx))
    prev_my = int(prev_my + SMOOTH * (my - prev_my))
    return prev_mx, prev_my

def get_finger_states(landmarks):
    tips = [4, 8, 12, 16, 20]
    states = []
    states.append(landmarks[4].x < landmarks[3].x)
    for tip in tips[1:]:
        states.append(landmarks[tip].y < landmarks[tip - 2].y)
    return states

def classify_gesture(states):
    thumb, index, middle, ring, pinky = states
    if index and not middle and not ring and not pinky:
        return "MOVE_CURSOR"
    elif index and middle and not ring and not pinky:
        return "SCROLL_UP"
    elif index and middle and ring and not pinky:
        return "SCROLL_DOWN"
    elif not index and not middle and not ring and not pinky:
        return "FIST"
    elif index and middle and ring and pinky:
        return "OPEN_HAND"
    else:
        return "UNKNOWN"

def run_gesture_module():
    # Use 640x480 — much faster for MediaPipe to process
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer lag

    print(f"Camera opened: {cap.isOpened()}")
    print("Gesture module running. Press 'q' to quit.")

    prev_gesture = ""
    last_click_time = 0
    fist_frame_count = 0
    frame_count = 0

    fps_counter = 0
    fps_display = 0
    fps_timer = time.time()

    last_landmarks = None  # Cache last known landmarks

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame_count += 1

        # Process MediaPipe only every 2nd frame — halves CPU load
        if frame_count % 2 == 0:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False
            result = hands.process(rgb)
            rgb.flags.writeable = True

            if result.multi_hand_landmarks:
                last_landmarks = result.multi_hand_landmarks[0]
            else:
                last_landmarks = None

        gesture = "NO HAND"

        if last_landmarks:
            mp_draw.draw_landmarks(
                frame, last_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                mp_draw.DrawingSpec(color=(255, 255, 255), thickness=2)
            )

            lm = last_landmarks.landmark
            states = get_finger_states(lm)
            gesture = classify_gesture(states)

            if gesture == "MOVE_CURSOR":
                fist_frame_count = 0
                index_tip = lm[8]
                raw_mx = int(index_tip.x * SCREEN_W)
                raw_my = int(index_tip.y * SCREEN_H)
                mx, my = smooth_cursor(raw_mx, raw_my)
                pyautogui.moveTo(mx, my)

            elif gesture == "SCROLL_UP":
                fist_frame_count = 0
                pyautogui.scroll(40)  # Increased from 25 to 40

            elif gesture == "SCROLL_DOWN":
                fist_frame_count = 0
                pyautogui.scroll(-40)  # Increased from -25 to -40

            elif gesture == "FIST":
                fist_frame_count += 1
                current_time = time.time()
                if fist_frame_count == 3 and (current_time - last_click_time) > 1.0:
                    pyautogui.click()
                    last_click_time = current_time
                    print(f"Click! at {time.strftime('%H:%M:%S')}")
            else:
                fist_frame_count = 0

            prev_gesture = gesture

        # FPS Counter
        fps_counter += 1
        if time.time() - fps_timer >= 1.0:
            fps_display = fps_counter
            fps_counter = 0
            fps_timer = time.time()

        # UI Overlay
        color = (0, 255, 0) if gesture != "NO HAND" else (0, 0, 255)
        cv2.putText(frame, f"Gesture: {gesture}", (10, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        cv2.putText(frame, f"FPS: {fps_display}", (10, 68),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 0), 2)

        if fist_frame_count > 0:
            cv2.putText(frame, f"Fist: {fist_frame_count}/3", (10, 98),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 165, 255), 2)

        cv2.imshow("Multimodal HCI - Gesture Module", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_gesture_module()