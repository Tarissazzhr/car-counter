from ultralytics import YOLO
import numpy as np
import cv2
import cvzone
import math
from sort import*

cap = cv2.VideoCapture("C:/Users/Tarisa/Visual Studio Code/cb/videos/vidjalan.mp4") #for video

model = YOLO("../yolo-weights/yolov8n.pt")

classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
              "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
              "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush"
              ]

mask = cv2.imread("C:/Users/Tarisa/Visual Studio Code/cb/car-counter/mask2.png")

#tracking
tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)

limits = [100,500,2000,500]
totalCount_car = []
totalCount_truck = []
totalCount_bus = []

while True:
    success, img = cap.read()
    if not success:
        break
        
    mask = cv2.resize(mask, (img.shape[1], img.shape[0]))
    imgRegion = cv2.bitwise_and(img,mask)
    if img.shape[:2] == mask.shape[:2]:
        imgRegion = cv2.bitwise_and(img, mask)
    else:
        print("Dimensi img dan mask tidak cocok!")
        break

    results = model(imgRegion, stream=True)

    detections = np.empty((0, 5))

    for r in results:
        boxes = r.boxes
        for box in boxes:
            # Bounding Box
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            # cv2.rectangle(img,(x1,y1),(x2,y2),(255,0,255),3)
            w, h = x2 - x1, y2 - y1
            cvzone.cornerRect(img,(x1,y1,w,h))
            #confidence
            conf = math.ceil((box.conf[0]*100))/100
            #class name
            cls = int(box.cls[0])
            currentClass = classNames[cls]

            if currentClass in ["car", "truck", "bus"] and conf > 0.3:
                # cvzone.putTextRect(img,f'{currentClass[cls]} {conf}',(max(0, x1), max(35, y1)),
                #                scale=1,thickness=1,offset=5)
                # cvzone.cornerRect(img,(x1,y1,w,h),l=9,rt=5)
                currentArray = np.array([x1,y1,x2,y2,conf])
                detections = np.vstack((detections,currentArray))
    
    resultsTracker = tracker.update(detections)
    cv2.line(img,(limits[0],limits[1]),(limits[2],limits[3]),(0,0,255),5)

    for result in resultsTracker:
        x1,y1,x2,y2,id = result
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        w, h = x2 - x1, y2 - y1
        cvzone.cornerRect(img,(x1,y1,w,h),l=9,rt=2,colorR=(255,0,255))
        cvzone.putTextRect(img,f'{currentClass} {conf}',(max(0, x1), max(35, y1)),
                               scale=2,thickness=3,offset=10)
        
        cx, cy = x1 + w // 2, y1 + h // 2
        cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

        if limits[0] < cx < limits[2] and limits[1] - 15 < cy < limits[1] + 15:
            if currentClass == "car" and totalCount_car.count(id) == 0:
                totalCount_car.append(id)
                cv2.line(img, (limits[0], limits[1]), (limits[2], limits[3]), (0, 255, 0), 5)
            elif currentClass == "truck" and totalCount_truck.count(id) == 0:
                totalCount_truck.append(id)
                cv2.line(img, (limits[0], limits[1]), (limits[2], limits[3]), (0, 255, 0), 5)
            elif currentClass == "bus" and totalCount_bus.count(id) == 0:
                totalCount_bus.append(id)
                cv2.line(img, (limits[0], limits[1]), (limits[2], limits[3]), (0, 255, 0), 5)
 
    cvzone.putTextRect(img, f'Car Count: {len(totalCount_car)}', (50, 50))
    cvzone.putTextRect(img, f'Truck Count: {len(totalCount_truck)}', (50, 100))
    cvzone.putTextRect(img, f'Bus Count: {len(totalCount_bus)}', (50, 150))

    cv2.imshow("Image", img)
    # cv2.imshow("ImageRegion", imgRegion)
    cv2.waitKey(1)
