import cv2
import mediapipe as mp
import math
import tkinter as tk
from PIL import Image, ImageTk

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

class ArmCurlCounter:
    def __init__(self):
        self.in_curl_position_left = False
        self.in_curl_position_right = False
        self.reps_count_left = 0
        self.reps_count_right = 0

    def calculate_angle(self, a, b, c):
        radians = math.atan2(c.y - b.y, c.x - b.x) - math.atan2(a.y - b.y, a.x - b.x)
        angle = abs(radians * 180.0 / math.pi)

        # Ensure we get the smaller angle
        if angle > 180.0:
            angle = 360 - angle

        return angle

    def process_frame(self, frame, landmarks):
        if len(landmarks) >= 16:  # Ensure there are enough landmarks for the arms
            left_shoulder = landmarks[mp_holistic.PoseLandmark.LEFT_SHOULDER]
            left_elbow = landmarks[mp_holistic.PoseLandmark.LEFT_ELBOW]
            left_wrist = landmarks[mp_holistic.PoseLandmark.LEFT_WRIST]

            right_shoulder = landmarks[mp_holistic.PoseLandmark.RIGHT_SHOULDER]
            right_elbow = landmarks[mp_holistic.PoseLandmark.RIGHT_ELBOW]
            right_wrist = landmarks[mp_holistic.PoseLandmark.RIGHT_WRIST]

            # Draw lines connecting body points
            self.draw_lines(frame, [(left_shoulder, left_elbow), (left_elbow, left_wrist),
                                    (right_shoulder, right_elbow), (right_elbow, right_wrist)])

            # Draw circles at the landmark positions
            self.draw_landmarks(frame, [left_shoulder, left_elbow, left_wrist, right_shoulder, right_elbow, right_wrist])

            # Calculate the angles for left and right arms
            left_arm_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
            right_arm_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)

            # Adjust the threshold based on your arm curl motion
            if left_arm_angle < 160:  # Adjusted threshold for better left-arm detection
                if not self.in_curl_position_left:
                    self.in_curl_position_left = True
                    self.reps_count_left += 1
            else:
                self.in_curl_position_left = False

            if right_arm_angle < 160:  # Adjusted threshold for better right-arm detection
                if not self.in_curl_position_right:
                    self.in_curl_position_right = True
                    self.reps_count_right += 1
            else:
                self.in_curl_position_right = False

        return self.in_curl_position_left or self.in_curl_position_right

    def draw_lines(self, frame, lines):
        for line in lines:
            cv2.line(frame, (int(line[0].x * frame.shape[1]), int(line[0].y * frame.shape[0])),
                     (int(line[1].x * frame.shape[1]), int(line[1].y * frame.shape[0])), (255, 0, 0), 3)

    def draw_landmarks(self, frame, landmarks):
        for landmark in landmarks:
            cx, cy = int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), cv2.FILLED)

class ArmCurlApp:
    def __init__(self, root, title):
        self.root = root
        self.root.title(title)
        self.video_source = 0
        self.vid = cv2.VideoCapture(self.video_source)

        self.arm_curl_counter = ArmCurlCounter()

        self.canvas = tk.Canvas(root, width=self.vid.get(cv2.CAP_PROP_FRAME_WIDTH), height=self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.pack()

        self.btn_exit = tk.Button(root, text="Exit", width=10, command=self.exit_app)
        self.btn_exit.pack(padx=20, pady=10)

        self.update()
        self.root.mainloop()

    def exit_app(self):
        self.vid.release()
        self.root.destroy()

    def update(self):
        ret, frame = self.vid.read()
        if self.arm_curl_counter.process_frame(frame, self.get_landmarks(frame)):
            reps_text = f"Left Arm Curls: {self.arm_curl_counter.reps_count_left} | Right Arm Curls: {self.arm_curl_counter.reps_count_right}"
        else:
            reps_text = "Arm Curls: 0"

        cv2.putText(frame, reps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 0, 0), 2)
        self.photo = self.convert_to_photo(frame)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.root.after(10, self.update)

    def get_landmarks(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(rgb_frame)
        return results.pose_landmarks.landmark if results.pose_landmarks else []

    def convert_to_photo(self, frame):
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        photo = ImageTk.PhotoImage(image=img)
        return photo

if __name__ == "__main__":
    holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    root = tk.Tk()
    app = ArmCurlApp(root, "POSE TRACK OF ARM CURL")
