import mediapipe as mp
import cv2 as cv
from scipy.spatial import distance as dis
import time

def draw_landmarks(image, outputs, land_mark, color):
    height, width = image.shape[:2]
             
    for face_landmarks in outputs.multi_face_landmarks:
        for face in land_mark:
            point = face_landmarks.landmark[face]
            point_scale = ((int)(point.x * width), (int)(point.y*height))
            cv.circle(image, point_scale, 2, color, 1)
            
def euclidean_distance(image, top, bottom):
    height, width = image.shape[0:2]
            
    point1 = int(top.x * width), int(top.y * height)
    point2 = int(bottom.x * width), int(bottom.y * height)
    
    distance = dis.euclidean(point1, point2)
    return distance

def get_aspect_ratio(image, outputs, top_bottom, left_right):
    aspect_ratios = []
    for face_landmarks in outputs.multi_face_landmarks:
        top = face_landmarks.landmark[top_bottom[0]]
        bottom = face_landmarks.landmark[top_bottom[1]]
        top_bottom_dis = euclidean_distance(image, top, bottom)
        
        left = face_landmarks.landmark[left_right[0]]
        right = face_landmarks.landmark[left_right[1]]
        left_right_dis = euclidean_distance(image, left, right)
        
        aspect_ratio = left_right_dis / top_bottom_dis
        aspect_ratios.append(aspect_ratio)
    return aspect_ratios


face_mesh = mp.solutions.face_mesh
draw_utils = mp.solutions.drawing_utils
landmark_style = draw_utils.DrawingSpec((0,255,0), thickness=1, circle_radius=1)
connection_style = draw_utils.DrawingSpec((0,0,255), thickness=1, circle_radius=1)


mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

STATIC_IMAGE_MODE = False
MAX_NUM_FACES = 5
DETECTION_CONFIDENCE = 0.6
TRACKING_CONFIDENCE = 0.6

COLOR_RED = (0, 0, 255)
COLOR_BLUE = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)

MOUTH_TOP_BOTTOM = [12,15]
MOUTH_LEFT_RIGHT = [78,308]

face_model = mp_face_mesh.FaceMesh(
    static_image_mode=STATIC_IMAGE_MODE,
    max_num_faces=MAX_NUM_FACES,
    min_detection_confidence=DETECTION_CONFIDENCE,
    min_tracking_confidence=TRACKING_CONFIDENCE)

capture = cv.VideoCapture(0)

frame_count = [0]*MAX_NUM_FACES
yawn_detect =[False]*MAX_NUM_FACES
yawning_faces =[]
min_frame = 6
min_tolerance = 1.8

while True:
    ret, image = capture.read()
    if not ret:
        break
    
    image_rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    results = face_model.process(image_rgb)

    if results.multi_face_landmarks:
        
        draw_landmarks(image, results, MOUTH_TOP_BOTTOM, COLOR_RED)
        draw_landmarks(image, results, MOUTH_LEFT_RIGHT, COLOR_RED)
        aspect_ratios = get_aspect_ratio(image, results, MOUTH_TOP_BOTTOM, MOUTH_LEFT_RIGHT)

        for idx, ratio in enumerate(aspect_ratios): 
            if ratio < min_tolerance:
                yawn_detect[idx]= True
                cv.putText(image, "Yawn Detected", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                yawn_detect[idx]= False

    timestamp = time.strftime("%H:%M:%S")
    print(f"{timestamp}")
    yawning_faces = [str(idx+1) for idx, detected in enumerate(yawn_detect) if detected]
    if yawning_faces:
        print("Drowsiness detected in face(s):", ", ".join(yawning_faces))

    cv.imshow('Face Mesh', image)
    if cv.waitKey(5) & 0xFF == 27:
        break

capture.release()
cv.destroyAllWindows()