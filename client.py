import cv2
import pickle
import socket
import struct
import imutils


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = '127.0.0.1'
port = 9999
client_socket.connect((server_ip, port))

vid = cv2.VideoCapture(0)
# vid = cv2.VideoCapture('video.mp4')

# Capture video and stream data
if client_socket:
    while vid.isOpened():
        try:
            img, frame = vid.read()
            frame = imutils.resize(frame, width=380)
            a = pickle.dumps(frame)
            message = struct.pack("Q", len(a)) + a
            client_socket.sendall(message)
            # cv2.imshow(f"TO: {host_ip}",frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                client_socket.close()
        except:
            print('VIDEO FINISHED!')
            break
