import cv2
import mediapipe as mp
import pyautogui
import numpy as np
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

def get_pinch_distance(landmarks):
    x1, y1 = landmarks[4].x, landmarks[4].y
    x2, y2 = landmarks[8].x, landmarks[8].y
    return np.hypot(x2 - x1, y2 - y1)

def classify_gesture(states, landmarks):
    thumb, index, middle, ring, pinky = states

    # --- DAY 2 gestures (order unchanged) ---
    if index and not middle and not ring and not pinky:
        return "MOVE_CURSOR"
    elif index and middle and not ring and not pinky:
        return "SCROLL_UP"
    elif index and middle and ring and not pinky:
        return "SCROLL_DOWN"
    elif not index and not middle and not ring and not pinky:
        # Distinguish FIST from PINCH
        if get_pinch_distance(landmarks) < 0.07:
            return "PINCH"
        return "FIST"
    elif index and middle and ring and pinky:
        return "OPEN_HAND"

    # --- DAY 3 new gestures ---
    elif pinky and not index and not middle and not ring:
        return "PINKY"

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
    frame_count = 0
    last_landmarks = None

    # --- DAY 2 state ---
    last_click_time = 0
    fist_frame_count = 0

    # --- DAY 3 state ---
    pinch_frame_count      = 0
    pinky_frame_count      = 0
    peace_frame_count      = 0
    drag_frame_count       = 0
    last_right_click_time  = 0
    last_double_click_time = 0
    last_esc_time          = 0
    dragging               = False

    fps_counter = 0
    fps_display = 0
    fps_timer = time.time()

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
            gesture = classify_gesture(states, lm)

            # =================================================================
            # DAY 2 ACTIONS — line for line unchanged
            # =================================================================

            if gesture == "MOVE_CURSOR":
                fist_frame_count  = 0
                peace_frame_count = 0
                pinch_frame_count = 0
                pinky_frame_count = 0
                drag_frame_count  = 0
                index_tip = lm[8]
                raw_mx = int(index_tip.x * SCREEN_W)
                raw_my = int(index_tip.y * SCREEN_H)
                mx, my = smooth_cursor(raw_mx, raw_my)
                pyautogui.moveTo(mx, my)
                if dragging:
                    pyautogui.mouseUp()
                    dragging = False

            elif gesture == "SCROLL_UP":
                fist_frame_count  = 0
                pinch_frame_count = 0
                pinky_frame_count = 0
                drag_frame_count  = 0
                peace_frame_count += 1
                pyautogui.scroll(40)
                # Day 3: same hand held 3 frames → double click
                current_time = time.time()
                if peace_frame_count == 3 and (current_time - last_double_click_time) > 1.2:
                    pyautogui.doubleClick()
                    last_double_click_time = current_time
                    gesture = "DOUBLE_CLICK"
                    print(f"Double click! at {time.strftime('%H:%M:%S')}")

            elif gesture == "SCROLL_DOWN":
                fist_frame_count  = 0
                peace_frame_count = 0
                pinch_frame_count = 0
                pinky_frame_count = 0
                drag_frame_count  = 0
                pyautogui.scroll(-40)

            elif gesture == "FIST":
                peace_frame_count = 0
                pinch_frame_count = 0
                pinky_frame_count = 0
                drag_frame_count  = 0
                fist_frame_count += 1
                current_time = time.time()
                if fist_frame_count == 3 and (current_time - last_click_time) > 1.0:
                    pyautogui.click()
                    last_click_time = current_time
                    print(f"Click! at {time.strftime('%H:%M:%S')}")

            elif gesture == "OPEN_HAND":
                fist_frame_count  = 0
                peace_frame_count = 0
                pinch_frame_count = 0
                pinky_frame_count = 0
                drag_frame_count += 1
                # Day 3: held 3 frames → drag mode
                if drag_frame_count >= 3:
                    if not dragging:
                        pyautogui.mouseDown()
                        dragging = True
                    index_tip = lm[8]
                    raw_mx = int(index_tip.x * SCREEN_W)
                    raw_my = int(index_tip.y * SCREEN_H)
                    mx, my = smooth_cursor(raw_mx, raw_my)
                    pyautogui.moveTo(mx, my)
                    gesture = "DRAG"

            # =================================================================
            # DAY 3 NEW ACTIONS
            # =================================================================

            elif gesture == "PINCH":
                fist_frame_count  = 0
                peace_frame_count = 0
                pinky_frame_count = 0
                drag_frame_count  = 0
                pinch_frame_count += 1
                current_time = time.time()
                if pinch_frame_count == 3 and (current_time - last_right_click_time) > 1.0:
                    pyautogui.rightClick()
                    last_right_click_time = current_time
                    print(f"Right click! at {time.strftime('%H:%M:%S')}")

            elif gesture == "PINKY":
                fist_frame_count  = 0
                peace_frame_count = 0
                pinch_frame_count = 0
                drag_frame_count  = 0
                pinky_frame_count += 1
                current_time = time.time()
                if pinky_frame_count == 3 and (current_time - last_esc_time) > 1.5:
                    pyautogui.press("esc")
                    last_esc_time = current_time
                    print(f"ESC pressed! at {time.strftime('%H:%M:%S')}")

            else:
                fist_frame_count  = 0
                peace_frame_count = 0
                pinch_frame_count = 0
                pinky_frame_count = 0
                drag_frame_count  = 0
                if dragging:
                    pyautogui.mouseUp()
                    dragging = False

            prev_gesture = gesture

        else:
            # No hand — reset everything, release drag
            fist_frame_count  = 0
            peace_frame_count = 0
            pinch_frame_count = 0
            pinky_frame_count = 0
            drag_frame_count  = 0
            if dragging:
                pyautogui.mouseUp()
                dragging = False

        # FPS Counter (Day 2 unchanged)
        fps_counter += 1
        if time.time() - fps_timer >= 1.0:
            fps_display = fps_counter
            fps_counter = 0
            fps_timer = time.time()

        # UI Overlay (Day 2 unchanged + new counters below)
        color = (0, 255, 0) if gesture != "NO HAND" else (0, 0, 255)
        cv2.putText(frame, f"Gesture: {gesture}", (10, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        cv2.putText(frame, f"FPS: {fps_display}", (10, 68),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 0), 2)

        if fist_frame_count > 0:
            cv2.putText(frame, f"Fist:  {fist_frame_count}/3", (10, 98),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 165, 255), 2)
        if pinch_frame_count > 0:
            cv2.putText(frame, f"Pinch: {pinch_frame_count}/3", (10, 128),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 165, 255), 2)
        if pinky_frame_count > 0:
            cv2.putText(frame, f"Pinky: {pinky_frame_count}/3", (10, 158),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 165, 255), 2)
        if peace_frame_count > 0:
            cv2.putText(frame, f"Peace: {peace_frame_count}/3", (10, 188),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 165, 255), 2)
        if dragging:
            cv2.putText(frame, "DRAG MODE ACTIVE", (10, 218),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)

        cv2.imshow("Multimodal HCI - Gesture Module", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    if dragging:
        pyautogui.mouseUp()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_gesture_module()