import socket
import pickle
import struct
import imutils
import threading
import cv2
import tkinter
import customtkinter as ctk
from PIL import Image, ImageTk
import ipaddress


host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
port = 9999


connected_clients = []


def check_ip(address):
    try:
        ipaddress.ip_address(address)
        return True
    except ValueError:
        return False


def update_clients():
    clients_count = len(connected_clients)
    info_label.configure(text=f"Connected Clients: {clients_count}")
    app.update()


def show_video(addr, client_socket, video_label, width, height):
    try:
        connected = True # indicate client connection
        if client_socket:  # if a client socket exists
            data = b""
            payload_size = struct.calcsize("Q")
            while connected:
                while len(data) < payload_size:
                    packet = client_socket.recv(4 * 1024)  # 4K max
                    if not packet:
                        connected = False
                        break
                    data += packet
                if not connected:
                    connected_clients.remove(addr)
                    update_clients()
                    break # exit loop if client disconnected
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

            # Change frame to a solid color when client disconnects
            disconnected_frame = Image.new('RGB', (width, height), color='#313335')
            photo = ctk.CTkImage(dark_image=disconnected_frame, size=(width, height))
            video_label.configure(image=photo)
            video_label.image = photo
            app.update()

    except Exception as e:
        connected_clients.remove(addr)
        update_clients()
        print(e)  # For debugging


def start_server(max_amount):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip_address = ip_address_input.get()
    socket_address = (ip_address, port)
    server_socket.bind(socket_address)
    server_socket.listen()
    print("Listening at", socket_address)

    while True:
        client_socket, addr = server_socket.accept()
        connected_clients.append(addr)
        update_clients()
        width, height = get_size()

        clients_count = len(connected_clients)
        video_label = set_video_label(clients_count)

        thread = threading.Thread(target=show_video, args=(addr, client_socket, video_label, width, height))
        thread.start()


def start_server_thread(max_amount):
    server_thread = threading.Thread(target=start_server, args=(max_amount,))
    server_thread.start()


def choose_grid():
    ip_address = ip_address_input.get()
    if not check_ip(ip_address):
        title.configure(text="Wrong IP address format!", text_color="red")
        return
    button.pack_forget()
    ip_address_input.pack_forget()
    title.configure(text="How many cameras do you want to connect?", text_color="white")
    button_wrapper.pack(pady=10, side="top")
    button_one.pack(side="left")
    button_two.pack(side="left", padx=(10,0))
    button_three.pack(side="left", padx=(10,0))
    button_four.pack(side="left", padx=(10,0))


def set_video_label(clients_count):
    video_labels = [video1, video2, video3, video4]
    if 1 <= clients_count <= 4:
        return video_labels[clients_count - 1]


def set_grid(amount):
    title.pack_forget()
    button_one.pack_forget()
    button_two.pack_forget()
    button_three.pack_forget()
    button_four.pack_forget()

    # Open fullscreen
    width = app.winfo_screenwidth()
    height = app.winfo_screenheight()
    app.geometry("%dx%d" % (width, height))
    app.after(0, lambda: app.state('zoomed'))

    app.columnconfigure(0, weight=1)
    app.columnconfigure(1, weight=1)
    app.rowconfigure(1, weight=1)

    info_wrapper.grid(row=0, column=0, pady=(0,20), sticky="ew", columnspan=2)
    info_subcontainer.pack(side="left")
    server_status.pack(side="left", padx=20)
    server_status.configure(text=f"Server is listening on: {ip_address_input.get()}")
    info_label.pack(side="left")

    if amount == 1:
        video1.grid(row=1, column=0, padx=20, pady=(0, 20), columnspan=2, sticky="nsew")
    if amount == 2:
        video1.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="nsew")
        video2.grid(row=1, column=1, padx=(10, 20), pady=(0, 20), sticky="nsew")
    if amount == 3 or amount == 4:
        app.rowconfigure(2, weight=1)
        video1.grid(row=1, column=0, padx=(20, 10), pady=(0, 10), sticky="nsew")
        video2.grid(row=1, column=1, padx=(10, 20), pady=(0, 10), sticky="nsew")
        video3.grid(row=2, column=0, padx=(20, 10), pady=(10, 20), sticky="nsew")
        video4.grid(row=2, column=1, padx=(10, 20), pady=(10, 20), sticky="nsew")

    width, height = get_size()

    video1.configure(width=width, height=height)
    video2.configure(width=width, height=height)
    video3.configure(width=width, height=height)
    video4.configure(width=width, height=height)


def get_size():
    app.update()

    width = video1.winfo_width()
    height = video1.winfo_height()

    return  width, height


def set_max_clients(amount):
    set_grid(amount)
    start_server_thread(amount)


# Initialize GUI
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
app = ctk.CTk()
app.title("CCTV")
app. geometry("720x480")


# IP config Page
container = ctk.CTkFrame(app, fg_color='transparent')
container.place(relx=0.5, rely=0.5, anchor='center')

title = ctk.CTkLabel(container, text="Configure CCTV Server IP ")
title.pack(pady=(0, 10))

entered_ip_address = tkinter.StringVar(value=host_ip)
ip_address_input = ctk.CTkEntry(container, width=200, height=40, textvariable=entered_ip_address)
ip_address_input.pack(pady=(0,5))

button = ctk.CTkButton(container, text="Select", command=choose_grid)
button.pack(pady=10)

# Grid Selection
button_wrapper = ctk.CTkFrame(container, fg_color='transparent')

button_one = ctk.CTkButton(button_wrapper, text="1", width=40, command=lambda:set_max_clients(1))
button_two = ctk.CTkButton(button_wrapper, text="2", width=40, command=lambda:set_max_clients(2))
button_three = ctk.CTkButton(button_wrapper, text="3", width=40, command=lambda:set_max_clients(3))
button_four = ctk.CTkButton(button_wrapper, text="4", width=40, command=lambda:set_max_clients(4))

# Video View
info_wrapper = ctk.CTkFrame(app, fg_color='#313335', height=40, corner_radius=0)
info_subcontainer = ctk.CTkFrame(info_wrapper, fg_color='transparent')
info_label = ctk.CTkLabel(info_subcontainer, fg_color='transparent', text="Connected Clients: 0")
server_status = ctk.CTkLabel(info_subcontainer, fg_color='transparent', text="")

video1 = ctk.CTkLabel(app, text="", fg_color='#313335')
video2 = ctk.CTkLabel(app, text="", fg_color='#313335')
video3 = ctk.CTkLabel(app, text="", fg_color='#313335')
video4 = ctk.CTkLabel(app, text="", fg_color='#313335')


# Run app
app.mainloop()

