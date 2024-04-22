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


connected_clients = []


def update_clients():
    clients_count = len(connected_clients)
    info_label.configure(text=f"Connected Clients: {clients_count}")
    app.update()


def show_video(addr, client_socket, video_label, width, height):
    try:
        print('CLIENT {} CONNECTED!'.format(addr))
        if client_socket:  # if a client socket exists
            data = b""
            payload_size = struct.calcsize("Q")
            while True:
                while len(data) < payload_size:
                    packet = client_socket.recv(4 * 1024)  # 4K max
                    if not packet:
                        break
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
                photo = ctk.CTkImage(dark_image=frame, size=(width, height))

                video_label.configure(image=photo)
                video_label.image = photo

                app.update()

            client_socket.close()
    except Exception as e:
        connected_clients.remove(addr)
        update_clients()
        print(e)  # For debugging
        print(f"CLIENT {addr} DISCONNECTED")



def start_server():
    title.pack_forget()
    button.pack_forget()
    container.pack_forget()

    app.columnconfigure(0, weight=1)
    app.columnconfigure(1, weight=1)
    app.rowconfigure(1, weight=1)
    app.rowconfigure(2, weight=1)
    info_label.grid(row=0, column=0, pady=20, sticky=ctk.N, columnspan=2)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # host_name = socket.gethostname()
    # host_ip = socket.gethostbyname(host_name)
    host_ip = '192.168.1.12'
    print('HOST IP:', host_ip)
    port = 9999
    socket_address = (host_ip, port)
    server_socket.bind(socket_address)
    server_socket.listen()
    print("Listening at", socket_address)

    while True:
        client_socket, addr = server_socket.accept()
        connected_clients.append(addr)
        update_clients()

        clients_count = len(connected_clients)
        width, height = update_grid(clients_count)
        video_label = set_video_label(clients_count)

        thread = threading.Thread(target=show_video, args=(addr, client_socket, video_label, width, height))
        thread.start()



def start_server_thread():
    server_thread = threading.Thread(target=start_server, args=())
    server_thread.start()


def set_video_label(clients_count):
    video_label = video1
    if (clients_count) == 2:
        video_label = video2
    return video_label

def update_grid(clients_count):

    # configure grid elements depending on clients_count
    video1.grid(row=1, column=0, padx=(20, 10), pady=(0, 10), sticky="nsew")
    video2.grid(row=1, column=1, padx=(10, 20), pady=(0, 10), sticky="nsew")
    video3.grid(row=2, column=0, padx=(20, 10), pady=(10, 20), sticky="nsew")
    video4.grid(row=2, column=1, padx=(10, 20), pady=(10, 20), sticky="nsew")

    app.update()

    width = video1.winfo_width()
    height = video1.winfo_height()

    video1.configure(width=width, height=height)
    video2.configure(width=width, height=height)
    video3.configure(width=width, height=height)
    video4.configure(width=width, height=height)

    return width, height


# Initialize GUI
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
app = ctk.CTk()
width = app.winfo_screenwidth()
height = app.winfo_screenheight()
app.geometry("%dx%d" % (width, height))
app.after(0, lambda: app.state('zoomed'))  # Open fullscreen
app.title("CCTV")

# Start Server Page
container = ctk.CTkFrame(app, fg_color='transparent')
container.place(relx=0.5, rely=0.5, anchor='center')

title = ctk.CTkLabel(container, text="Start CCTV Server")
title.pack(pady=(0, 10))

button = ctk.CTkButton(container, text="Start", command=start_server_thread)
button.pack(pady=10)

# Video View
info_label = ctk.CTkLabel(app, fg_color='transparent', text=f"Connected Clients: 0")

video1 = ctk.CTkLabel(app, text="", fg_color='#313335')
video2 = ctk.CTkLabel(app, text="", fg_color='#313335')
video3 = ctk.CTkLabel(app, text="", fg_color='#313335')
video4 = ctk.CTkLabel(app, text="", fg_color='#313335')

# Run app
app.mainloop()