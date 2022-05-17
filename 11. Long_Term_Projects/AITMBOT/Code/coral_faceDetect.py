import numpy as np
import cv2
import time
from PIL import Image
from edgetpu.detection.engine import DetectionEngine
import amg8833_i2c
import Thermal

# from coral homepage
model = "mobilenet_ssd_v2_face_quant_postprocess_edgetpu.tflite"
label_path = "face_labels.txt"

# model Object activate
engine = DetectionEngine(model)

labels = {}
box_colors = {}
prevTime = 0

# read label
with open(label_path, 'r') as f:
    lines = f.readlines()
    for line in lines:    
        id, name = line.strip().split(maxsplit=1)   
        labels[int(id)] = name
print(f"Model loaded({model}) \nTrained object({len(labels)}):\n{labels.values()}")
print("Quit to ESC.")

cap = cv2.VideoCapture(-1)
while True:
    ret, frame = cap.read()
    if not ret:
        print("cannot read frame.")
        break
    # BGR 2 RGB
    img = frame[:, :, ::-1].copy() 
    # array to PILimage
    img = Image.fromarray(img)  

    # threshold=0.5: mininum confidence , top_k=5 : maximum number of detected object 
    candidates = engine.detect_with_image(img, threshold=0.5, top_k=5, keep_aspect_ratio=True, relative_coord=False, )
    if candidates:
        for obj in candidates:
            if obj.label_id in box_colors:
                box_color = box_colors[obj.label_id] # the same color for the same object
            else :
                box_color = [int(j) for j in np.random.randint(0,255, 3)] # random color for new object
                box_colors[obj.label_id] = box_color

            # drawing bounding-box
            box_left, box_top, box_right, box_bottom = tuple(map(int, obj.bounding_box.ravel()))
            # temp check activate
            Thermal.interp(box_left, box_top, box_right, box_bottom)
            cv2.rectangle(frame, (box_left, box_top), (box_right, box_bottom), box_color, 2)

            # drawing label box
            accuracy = int(obj.score * 100)
            label_text = labels[obj.label_id] + " (" + str(accuracy) + "%)" 
            (txt_w, txt_h), base = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_PLAIN, 2, 3)
            cv2.rectangle(frame, (box_left - 1, box_top - txt_h), (box_left + txt_w, box_top + txt_h), box_color, -1)
            cv2.putText(frame, label_text, (box_left, box_top+base), cv2.FONT_HERSHEY_PLAIN, 2, (255,255,255), 2)

    # calculating and drawing fps            
    currTime = time.time()
    fps = 1/ (currTime -  prevTime)
    prevTime = currTime
    cv2.putText(frame, "fps:%.1f"%fps, (10,30), cv2.FONT_HERSHEY_PLAIN, 2, (0,255,0), 2)
    cv2.imshow('Object Detecting', frame)
    if cv2.waitKey(1)&0xFF == 27:
        break  
cap.release()
