# CCTV Control Panel
<i>Project done for the subject audio-video streaming </i> <br/>

## About
The main idea was to create a system with a graphical interface allowing for 
viewing images from many IP cameras connected to one server using a web socket.

## User Interface 
<i>Comming soon...</i>

## How it works?

### Client
- Video frames from webcam are captured using OpenCV.
- Pickle module is used to serialize frame to bytes.
- Each frame data is packed using Struct module.
- Packed bytes are sent to the server socket.
  
### Server
- Server socket is listening on selected address and port number.
- Each accepted client connection start a new thread used to process video packets.
- Data from each client is unpacked using Struct module and assembled into frame using Pickle module.
- Video frame is converted from BGR to RGB color space and displayed in GUI.
- Each received video can be recorded independently. 
- Recordings are saved to the appropriate folder, with a name that clearly indicate the time and source of the recording.
  
## Technology Stack

[Python 🔗](https://www.python.org)<br>
[Customtkinter🔗](https://github.com/TomSchimansky/CustomTkinter)<br>
[OpenCV🔗](https://opencv.org)<br>
[Pillow🔗](https://pillow.readthedocs.io/en/stable/installation/index.html)<br>

## Transport Layer protocol
- In most cases of live video streaming, UDP is the best solution. Delivery time is the most important thing, and losing a few packages is acceptable.
- However, this project uses the TCP protocol.
- Server do not use multicast transmission to stream any data to clients. Each client sends data to the server individually - it is a unicast connection each time, so using TCP is possible. 
- The advantage of this solution is that the connection is constantly monitored, so when one of the clients disconnects, it is immediately visible in the control panel. However, this results in slower transmission and higher bandwidth usage.
- In addition, videos from IP cameras can be recorded and stored in the server's mass storage, so that they can then be thoroughly analyzed. Therefore, it is crucial that the server receives all the frames without artifacts.

## Installation Guide 

Here's a step-by-step guide to help you get started with the project.

### Prerequisites

Before you begin, make sure you have the following installed on your machine:

- Python (version 3.13 or later)
- pip package manager (version 24.0 or later)

### Installation

Let's start with installing all dependencies that are not pre-packaged with Python. Move to the app main workspace and run:

    pip install customtkinter
    pip install opencv-python
    pip install pillow

To run server or client script from the command line, in the app workspace type:

    python scriptName.py 


