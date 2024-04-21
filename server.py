import socket
import pickle
import struct
import imutils
import threading
import pyshine as ps
import cv2
import tkinter
import customtkinter as ctk
from PIL import Image, ImageTk


def show_video(addr, client_socket):
    try:
        print('CLIENT {} CONNECTED!'.format(addr))
        if client_socket:  # if a client socket exists
            data = b""
            payload_size = struct.calcsize("Q")
            while True:
                while len(data) < payload_size:
                    packet = client_socket.recv(4 * 1024)  # 4K max
                    if not packet: break
                    data += packet
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q", packed_msg_size)[0]

                while len(data) < msg_size:
                    data += client_socket.recv(4 * 1024)
                frame_data = data[:msg_size]
                data = data[msg_size:]
                frame = pickle.loads(frame_data)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # convert from BGR to RGB
                frame = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image=frame)
                video.configure(image=photo)
                video.image = photo
                title.configure(text="Video Open!", text_color="green")
                app.update()
    except Exception as e:
        print(e) # For debugging
        print(f"CLINET {addr} DISCONNECTED")
        pass


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # host_name = socket.gethostname()
    # host_ip = socket.gethostbyname(host_name)
    host_ip = '127.0.0.1'
    print('HOST IP:', host_ip)
    port = 9999
    socket_address = (host_ip, port)
    server_socket.bind(socket_address)
    server_socket.listen()
    print("Listening at", socket_address)
    title.configure(text="Server Started!", text_color="green")
    app.update()
    while True:
        client_socket, addr = server_socket.accept()
        thread = threading.Thread(target=show_video, args=(addr, client_socket))
        thread.start()
        print("TOTAL CLIENTS ", threading.activeCount() - 2)


def start_server_thread():
    server_thread = threading.Thread(target=start_server, args=())
    server_thread.start()


# Initialize GUI
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
app = ctk.CTk()
width = app.winfo_screenwidth()
height = app.winfo_screenheight()
app.geometry("%dx%d" % (width, height))
app.after(0, lambda: app.state('zoomed'))  # Open fullscreen
app.title("CCTV")

title = ctk.CTkLabel(app, text="Test")
title.pack(pady=(0, 10))
button = ctk.CTkButton(app, text="Start Server", command=start_server_thread)
button.pack(pady=10)
video = ctk.CTkLabel(app, text="")
video.pack()

# Run app
app.mainloop()

