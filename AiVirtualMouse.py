import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy
import pyautogui

##########################
wCam, hCam = 1280, 720
frameR = 100  # Frame Reduction
smoothening = 5
#########################

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()
# print(wScr, hScr)


while True:
    # 1.寻找手部坐标
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

        # 2.获取食指中指指尖坐标
    if len(lmList) != 0:
        x0, y0 = lmList[4][1:]
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        # print(x1, y1, x2, y2)

    # 3. 检查指尖状态
    fingers = detector.fingersUp()
    # print(fingers)
    cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                  (255, 0, 255), 2)
    # 4. 食指朝上: 移动模式
    if fingers[1] == 1:
    #if fingers[1] == 1 and fingers[2] == 0:
        # 5.坐标转换
        x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
        y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
        # 6. 平滑处理
        clocX = plocX + (x3 - plocX) / smoothening
        clocY = plocY + (y3 - plocY) / smoothening

        # 7. 移动鼠标
        autopy.mouse.move(wScr - clocX, clocY)
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        plocX, plocY = clocX, clocY

    # 8.大拇指抬起进入点击模式
    if fingers[0] == 1 and fingers[1] == 1:
        # 9.检查指尖距离
        length, img, lineInfo = detector.findDistance(8, 4, img)
        print(length)
        # 10.距离过短单击鼠标
        is_mouse_down = False
        if length < 40:
            cv2.circle(img, (lineInfo[4], lineInfo[5]),
                       15, (0, 255, 0), cv2.FILLED)
            autopy.mouse.click()
            #if not is_mouse_down:
            #    pyautogui.mouseDown(button='left')
            #    is_mouse_down = True
            #else:
            #    if is_mouse_down:
            #        pyautogui.mouseUp(button='left')
            #        is_mouse_down = False

    # 11. 帧数显示
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 0), 3)
    # 12. 显示
    cv2.imshow("Image", img)
    cv2.waitKey(1)