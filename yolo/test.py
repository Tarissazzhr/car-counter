from ultralytics import YOLO
import cv2
 
model = YOLO('../yolo-weights/yolov8l.pt')
results = model("C:/Users/Tarisa/Visual Studio Code/cb/yolo/images/1.png", show=True)
cv2.waitKey(0)