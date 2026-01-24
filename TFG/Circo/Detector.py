import cv2
import mediapipe as mp


# https://google.github.io/mediapipe/solutions/pose

class Detector:
    def __init__(self, mode):
        self. mode = mode
        if self.mode == 'hand':
            self.mp_drawing = mp.solutions.drawing_utils
            self.mp_drawing_styles = mp.solutions.drawing_styles
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                model_complexity=0,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5)

        else:
            self.mp_drawing = mp.solutions.drawing_utils
            self.mp_drawing_styles = mp.solutions.drawing_styles
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                static_image_mode=True,
                model_complexity=2,
                enable_segmentation=True,
                min_detection_confidence=0.5)

    def __prepareBody(self, image):
        '''Prepare a list with the marks of 33 pose landmarks
        if no pose is detected the list in empty.
        Each mark is represented by (x,y), being x and y
        normalized to [0.0, 1.0] by the image width and height respectively.
        The function returns also the image including the drawing of detected
        pose landmarks and conecting lines'''

        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image)
        image.flags.writeable = True

        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        self.mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            self.mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style())
        poseLandmarks = []
        if results.pose_landmarks:
            for landmark in results.pose_landmarks.landmark:
                poseLandmarks.append([landmark.x, landmark.y])
        if self.mode == 'half body':
            poseLandmarks = poseLandmarks[11:25]
        return poseLandmarks, image



    def __prepareHand(self, image):
        '''Prepare two lists of marks, one for each hand (left and right)
        if one of the hands (or both) is not detected the corresponding list in empty.
        Each list has 21 marks corresponding to 21  hand-knuckles.
        Each mark is represented by (x,y), being x and y
        normalized to [0.0, 1.0] by the image width and height respectively.
        The function returns also the image including the drawing of detected
        hand-knuckles and conecting lines'''
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image)

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        leftHandLandmarks = []
        rightHandLandmarks = []

        if results.multi_hand_landmarks:

            for hand_landmarks in results.multi_hand_landmarks:

                # Get hand index to check label (left or right)
                handIndex = results.multi_hand_landmarks.index(hand_landmarks)
                handLabel = results.multi_handedness[handIndex].classification[0].label
                # Set variable to keep landmarks positions (x and y)
                if handLabel == "Left":
                    # Fill list with x and y positions of each landmark
                    for landmarks in hand_landmarks.landmark:
                        leftHandLandmarks.append([landmarks.x, landmarks.y])
                '''
                if handLabel == "Right":
                    # Fill list with x and y positions of each landmark
                    for landmarks in hand_landmarks.landmark:
                        rightHandLandmarks.append([landmarks.x, landmarks.y])
                '''
                # draw hand-knuckles and conecting lines in image
                if handLabel == "Left":
                    self.mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style())

        return leftHandLandmarks, image


    def normalize(self, r):
        size = 10
        minx = 2
        miny = 2
        maxx = -1
        maxy = -1
        for point in r:
            if point[0] < minx:
                minx = point[0]
            if point[1] < miny:
                miny = point[1]
            if point[0] > maxx:
                maxx = point[0]
            if point[1] > maxy:
                maxy = point[1]

        for point in r:
            point[0] = point[0] - minx
            point[1] = point[1] - miny

        width = maxx - minx
        height = maxy - miny

        for point in r:
            point[0] = point[0] * size // width + 3
            point[1] = point[1] * size // height + 3

        return r

    def pointInCicle (self, point, center, radious):
        if (point[0]*40 - center[0]*40)*(point[0]*40 - center[0]*40) + (point[1]*40 - center[1]*40)*(point[1]*40 - center[1]*40) <= (radious*radious):
            return True
        else:
            return False

    def detectPose(self, norm, p, accuracy):
        if self.mode == 'hand':
            points = [0,4,8,12,16,20]

            #for i in range(0, len(norm)):
            for i in points:
                if not self.pointInCicle(norm[i], self.poseList[p][i], accuracy):
                    return False
            return True
        else:
            points = [0,1,2,3,4,5,12,13]
            #for i in range(0, len(norm)):
            for i in points:
                if not self.pointInCicle(norm[i], self.poseList[p][i], accuracy):
                    return False
            return True


    def markImage(self, image):
        if self.mode == 'hand':
            landmarks, image = self.__prepareHand(image)
        else:
            landmarks, image = self.__prepareBody(image)
        return landmarks, image



    def markImage1 (self, image, p, accuracy):
        color = (255, 0, 0)
        #for i in range(0, len(self.poseList[p])):
        for i in [0, 1, 2, 3, 4, 5, 12, 13]:
            image = cv2.circle(image, (int(self.poseList[p][i][0])*40,int(self.poseList[p][i][1])*40), accuracy, color, 2)
            cv2.putText(image, str (i+11), (int(self.poseList[p][i][0])*40,int(self.poseList[p][i][1])*40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)

        return image
    def markImage2 (self, markedImage, norm ):
        color = (255, 0, 0)
        '''    for i in range(0, len(norm)):
            markedImage = cv2.circle(markedImage, (int(norm[i][0])*40,int(norm[i][1])*40),10, (0,0,255), -1)'''
        markedImage = cv2.circle(markedImage, (int(norm[0][0]) * 40, int(norm[0][1]) * 40), 10, (0, 0, 255), -1)
        markedImage = cv2.circle(markedImage, (int(norm[1][0]) * 40, int(norm[1][1]) * 40), 10, (0, 0, 255), -1)
        markedImage = cv2.circle(markedImage, (int(norm[2][0]) * 40, int(norm[2][1]) * 40), 10, (0, 0, 255), -1)
        markedImage = cv2.circle(markedImage, (int(norm[3][0]) * 40, int(norm[3][1]) * 40), 10, (0, 0, 255), -1)
        markedImage = cv2.circle(markedImage, (int(norm[4][0]) * 40, int(norm[4][1]) * 40), 10, (0, 0, 255), -1)
        markedImage = cv2.circle(markedImage, (int(norm[5][0]) * 40, int(norm[5][1]) * 40), 10, (0, 0, 255), -1)

        markedImage = cv2.circle(markedImage, (int(norm[12][0]) * 40, int(norm[12][1]) * 40), 10, (0, 0, 255), -1)
        markedImage = cv2.circle(markedImage, (int(norm[13][0]) * 40, int(norm[13][1]) * 40), 10, (0, 0, 255), -1)

        cv2.line(markedImage, (int(norm[0][0]) * 40, int(norm[0][1]) * 40), (int(norm[1][0]) * 40, int(norm[1][1]) * 40), (255, 0, 0), 5)

        cv2.line(markedImage, (int(norm[0][0]) * 40, int(norm[0][1]) * 40), (int(norm[2][0]) * 40, int(norm[2][1]) * 40), (255, 0, 0), 5)

        cv2.line(markedImage, (int(norm[2][0]) * 40, int(norm[2][1]) * 40), (int(norm[4][0]) * 40, int(norm[4][1]) * 40), (255, 0, 0), 5)

        cv2.line(markedImage, (int(norm[0][0]) * 40, int(norm[0][1]) * 40), (int(norm[12][0]) * 40, int(norm[12][1]) * 40), (255, 0, 0), 5)

        cv2.line(markedImage, (int(norm[12][0]) * 40, int(norm[12][1]) * 40), (int(norm[13][0]) * 40, int(norm[13][1]) * 40), (255, 0, 0), 5)

        cv2.line(markedImage, (int(norm[1][0]) * 40, int(norm[1][1]) * 40), (int(norm[13][0]) * 40, int(norm[13][1]) * 40), (255, 0, 0), 5)

        cv2.line(markedImage, (int(norm[1][0]) * 40, int(norm[1][1]) * 40), (int(norm[3][0]) * 40, int(norm[3][1]) * 40), (255, 0, 0), 5)
        cv2.line(markedImage, (int(norm[3][0]) * 40, int(norm[3][1]) * 40), (int(norm[5][0]) * 40, int(norm[5][1]) * 40), (255, 0, 0), 5)
        minx = 2000
        miny = 2000
        maxx = -1
        maxy = -1
        for i in [0,1,2,3,4,5,12,13]:
            if norm[i][0] < minx:
                minx = norm[i][0]
            if norm[i][1] < miny:
                miny = norm[i][1]
            if norm[i][0] > maxx:
                maxx = norm[i][0]
            if norm[i][1] > maxy:
                maxy = norm[i][1]
        #cv2.rectangle(markedImage, (int(minx)*40, int(miny)*40), (int(maxx)*40, int(maxy)*40), (0, 255, 0), 3)

        return markedImage


    def detect(self, image, accuracy):

        landmarks, image = self.markImage(image)

        '''markedImage = image
        markedImage = cv2.resize(markedImage, (800, 600))
        markedImage = self.markImage1(markedImage, 0, accuracy)'''
        res = ''
        if len(landmarks) > 0:
            norm = self.normalize(landmarks)
            '''markedImage = self.markImage2(markedImage, norm)
            cv2.imshow('marked', markedImage)'''

            for p in range(0, len(self.poseList)):
                if self.detectPose(norm, p, accuracy):
                    res = p + 1
                    break
        return res, image
    def storePoses (self, poseList):
        self.poseList = poseList

    def getPoses (self):
        return self.poseList
