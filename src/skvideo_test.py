import cv2 as cv
import skvideo.io
import numpy as np

cap = cv.VideoCapture(0)

outputfile = "test.mp4"
# outputdata = np.random.random(size=(30, 480, 680, 3)) * 255
# outputdata = outputdata.astype(np.uint8)

# start the FFmpeg writing subprocess with following parameters
writer = skvideo.io.FFmpegWriter(outputfile, outputdict={
  '-vcodec': 'libx264',
  '-preset': 'ultrafast',
  '-crf': '22',
  '-g': '30',
  '-framerate': '30',
  '-r': '30',
  '-keyint_min': '30',
  '-sc_threshold': '0'
})

# for i in range(30):
#   writer.writeFrame(outputdata[i])
# writer.close()

# -preset ultrafast -crf 22 -g FPS -keyint_min FPS -sc_threshold 0

count = 0
while(True or count > 10000):
    count += 1
    ret, frame = cap.read()
    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    writer.writeFrame(frame)
    cv.imshow('frame', frame)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
