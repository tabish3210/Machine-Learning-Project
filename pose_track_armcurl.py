import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

class ArmCurlCounter:
    def __init__(self):
        self.in_curl_position = False
        self.reps_count = 0

    def process_frame(self, frame, landmarks):
        left_shoulder_y = landmarks[mp_holistic.PoseLandmark.LEFT_SHOULDER].y
        left_wrist_y = landmarks[mp_holistic.PoseLandmark.LEFT_WRIST].y

        # Adjust the threshold based on your arm curl motion
        if left_wrist_y > left_shoulder_y + 0.03:  # Adjusted threshold for better left-hand detection
            if not self.in_curl_position:
                self.in_curl_position = True
                self.reps_count += 1
        else:
            self.in_curl_position = False

        return frame

def main():
    cap = cv2.VideoCapture(0)

    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        curl_counter = ArmCurlCounter()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = holistic.process(rgb_frame)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                frame = curl_counter.process_frame(frame, landmarks)

                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
                
                # Display zero reps if no arm curls detected, otherwise display the current reps count
                reps_text = f"Arm Curls: {curl_counter.reps_count}" if curl_counter.in_curl_position else "Arm Curls: 0"
                # Change text color to dark blue (BGR format)
                cv2.putText(frame, reps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 0, 0), 2)

            cv2.imshow('Arm Curl Repetition Counter', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
