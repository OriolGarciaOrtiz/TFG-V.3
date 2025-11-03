import cv2 as cv
import mediapipe as mp


def initialize ():
    global pose
    global mp_drawing
    global mp_drawing_styles
    global mp_pose

    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            enable_segmentation=True,
            min_detection_confidence=0.5)


def prepareBody(image):
    global pose
    global mp_drawing
    global mp_drawing_styles
    global mp_pose


    image.flags.writeable = False
    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    results = pose.process(image)
    image.flags.writeable = True

    image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
    mp_drawing.draw_landmarks(
        image,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
    bodyLandmarks = []
    if results.pose_landmarks:
        for landmark in results.pose_landmarks.landmark:
            bodyLandmarks.append([landmark.x, landmark.y])
    return bodyLandmarks, image


cap = cv.VideoCapture(0)
initialize()

while True:
    result, computerFrame = cap.read()
    if result:
        computerFrame = cv.resize(computerFrame, (720,480))
        bodyLandmarks, frameWithLandmarks = prepareBody(computerFrame)
        print('coordenada X del punto 20: ', bodyLandmarks[20][0])
        print('coordenada Y del punto 20: ', bodyLandmarks[20][1])
        #Lo raro es que me está detectando coordenadas más grandes que 1
        if len(bodyLandmarks) > 13:
            if bodyLandmarks[13][1] < bodyLandmarks[11][1]:
                print("¡Brazo derecho levantado!")
            else:
                print("Brazo derecho no está levantado.")
        cv.imshow("computer", frameWithLandmarks)
        cv.waitKey(1)