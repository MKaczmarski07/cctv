import cv2
import pickle
import socket
import struct


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = '127.0.0.1'
port = 9999
client_socket.connect((server_ip, port))

vid = cv2.VideoCapture(0)

# Capture video and stream data
if client_socket:
    while vid.isOpened():
        try:
            img, frame = vid.read()
            a = pickle.dumps(frame)
            message = struct.pack("Q", len(a)) + a
            client_socket.sendall(message)
            # cv2.imshow(f"TO: {host_ip}",frame)
            # key = cv2.waitKey(1) & 0xFF
            # if key == ord("q"):
            #     client_socket.close()
        except:
            print('VIDEO STREAMING FINISHED!')
            break
