import socket
import pickle
import struct
import threading
import cv2
import tkinter
import customtkinter as ctk
from PIL import Image
import ipaddress
import os
import datetime


host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
port = 9999


connected_clients = []
recording_status = {} # {client_id: state}


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


def configure_file(addr):
    now = datetime.datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    recordings_dir = "recordings"
    if not os.path.exists(recordings_dir):
        os.makedirs(recordings_dir)
    folder_name = os.path.join(recordings_dir, date_str)
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    file_name = f"{addr[0]}_{now.strftime('%H%M%S')}.mp4"
    return os.path.join(folder_name, file_name)


def toggle_recording(client_id, record_button):
    recording_status[client_id] = not recording_status.get(client_id, False)
    if recording_status[client_id]:
        record_button.configure(fg_color='green', hover_color='green')
    else:
        record_button.configure(fg_color='red', hover_color='red')


def show_video(addr, client_socket, video_label, record_button, width, height):
    try:
        connected = True # indicate client connection
        writer = None
        client_id = addr[1]  # Use client port number as unique ID
        recording_status[client_id] = False
        record_button.configure(command=lambda: toggle_recording(client_id, record_button))

        current_day = datetime.datetime.now().day

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

                if recording_status[client_id]:
                    if writer is None:
                        frame_height, frame_width = frame.shape[:2]
                        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
                        file_name = configure_file(addr)
                        writer = cv2.VideoWriter(file_name, fourcc, 20.0, (frame_width, frame_height))

                    writer.write(frame)

                if writer is not None and recording_status[client_id] == False:
                    writer.release()
                    writer = None


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
    finally:
        if writer is not None:
            writer.release()


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
        video_label, record_button = set_view(clients_count)

        thread = threading.Thread(target=show_video, args=(addr, client_socket, video_label, record_button, width, height))
        thread.start()


def start_server_thread(max_amount):
    server_thread = threading.Thread(target=start_server, args=(max_amount,))
    server_thread.start()


def choose_grid():
    ip_address = ip_address_input.get()
    if not check_ip(ip_address):
        title.configure(text="Wrong IP address format!", text_color="red")
        return
    select_button.pack_forget()
    ip_address_input.pack_forget()
    title.configure(text="How many cameras do you want to connect?", text_color="white")
    button_wrapper.pack(pady=10, side="top")
    buttons = [button_one, button_two, button_three, button_four]
    for btn in buttons:
        if btn == button_one:
            btn.pack(side="left")
        else:
            btn.pack(side="left", padx=(10,0))


def set_view(clients_count):
    video_labels = [video1, video2, video3, video4]
    record_buttons = [rec_button1, rec_button2, rec_button3, rec_button4]
    if 1 <= clients_count <= 4:
        return video_labels[clients_count - 1], record_buttons[clients_count - 1]


def set_grid(amount):
    elements_to_forget = [title, button_one, button_two, button_three, button_four]
    for element in elements_to_forget:
        element.pack_forget()

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
        rec_button1.place(in_=video1, relx=1, x=-20, y=20, anchor='ne')
    if amount == 2:
        video1.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="nsew")
        video2.grid(row=1, column=1, padx=(10, 20), pady=(0, 20), sticky="nsew")
        rec_button1.place(in_=video1, relx=1, x=-20, y=20, anchor='ne')
        rec_button2.place(in_=video2, relx=1, x=-20, y=20, anchor='ne')
    if amount == 3 or amount == 4:
        app.rowconfigure(2, weight=1)
        video1.grid(row=1, column=0, padx=(20, 10), pady=(0, 10), sticky="nsew")
        video2.grid(row=1, column=1, padx=(10, 20), pady=(0, 10), sticky="nsew")
        video3.grid(row=2, column=0, padx=(20, 10), pady=(10, 20), sticky="nsew")
        video4.grid(row=2, column=1, padx=(10, 20), pady=(10, 20), sticky="nsew")
        rec_button1.place(in_=video1, relx=1, x=-20, y=20, anchor='ne')
        rec_button2.place(in_=video2, relx=1, x=-20, y=20, anchor='ne')
        rec_button3.place(in_=video3, relx=1, x=-20, y=20, anchor='ne')
        rec_button4.place(in_=video4, relx=1, x=-20, y=20, anchor='ne')

    width, height = get_size()
    video_labels = [video1, video2, video3, video4]
    for label in video_labels:
        label.configure(width=width, height=height)


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

select_button = ctk.CTkButton(container, text="Select", command=choose_grid)
select_button.pack(pady=10)


# Grid Selection Page
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

video1 = ctk.CTkLabel(app)
video2 = ctk.CTkLabel(app)
video3 = ctk.CTkLabel(app)
video4 = ctk.CTkLabel(app)
video_labels = [video1, video2, video3, video4]
for label in video_labels:
    label.configure(text="", fg_color='#313335')

rec_button1 = ctk.CTkButton(app)
rec_button2 = ctk.CTkButton(app)
rec_button3 = ctk.CTkButton(app)
rec_button4 = ctk.CTkButton(app)

rec_buttons = [rec_button1, rec_button2, rec_button3, rec_button4]
for btn in rec_buttons:
    btn.configure(text="", height=20, width=20, corner_radius=5, fg_color='red', border_width=1.5, border_color='white', hover_color='red')


# Run app
app.mainloop()
