import cv2
import numpy as np
from flask import Flask,request
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

net = cv2.dnn.readNet('yolov3_training_last.weights','yolov3_testing.cfg')
# use gpu for faster processing - custom opencv compiled from sources with cuda enabled
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)

classes = []
with open("classes.txt", "r") as f:
    classes = f.read().splitlines()

# cap = cv2.VideoCapture('http://192.168.1.2:4747/video')
# cap = cv2.VideoCapture('http://192.168.1.3:8080/?action=stream')
cap = cv2.VideoCapture(1)
font = cv2.FONT_HERSHEY_PLAIN
colors = np.random.uniform(0, 255, size=(100, 3))

@socketio.on('server')
def checkMask():
  while (True):
    _, img = cap.read()
    height, width, _ = img.shape
    blob = cv2.dnn.blobFromImage(img, 1/255, (416, 416), (0,0,0), swapRB=True, crop=False)
    net.setInput(blob)
    output_layers_names = net.getUnconnectedOutLayersNames()
    layerOutputs = net.forward(output_layers_names)
    boxes = []
    confidences = []
    class_ids = []
    for output in layerOutputs:
          for detection in output:
              scores = detection[5:]
              class_id = np.argmax(scores)
              confidence = scores[class_id]
              if confidence > 0.2:
                  center_x = int(detection[0]*width)
                  center_y = int(detection[1]*height)
                  w = int(detection[2]*width)
                  h = int(detection[3]*height)
                  x = int(center_x - w/2)
                  y = int(center_y - h/2)
                  boxes.append([x, y, w, h])
                  confidences.append((float(confidence)))
                  class_ids.append(class_id)
    
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.2, 0.4)
    if len(indexes)>0:
          for i in indexes.flatten():
              x, y, w, h = boxes[i]
              label = str(classes[class_ids[i]])
              confidence = str(round(confidences[i],2))
              color = colors[i]
              cv2.rectangle(img, (x,y), (x+w, y+h), color, 2)
              cv2.putText(img, label + " " + confidence, (x,  y+20), font, 2, (255,255,255), 2)
              if label == 'wearing_mask':
                socketio.emit('gateStatus', 'open')
               
              elif label == 'not_wearing_mask':
                socketio.emit('gateStatus', 'close')
                # socketio.sleep(0)
                # second = False
              # continue
    cv2.imshow('Image', img)
    if cv2.waitKey(27) == ord('a'):
      cap.release()
      cv2.destroyAllWindows()

    socketio.sleep(0)


@socketio.on('connect')
def connect():
    print('middleman connected',request.sid)

if __name__ == '__main__':
    try:
        socketio.run(app,port=5000, host='0.0.0.0')
        # checkMask()
    except Exception as e:
        print("\n Execption occurs while starting the socketio server",str(e))


# checkMaskOnFace()
