# CCTV Server
<i>Project done for the subject audio-video streaming </i> <br/>

## About
The main idea was to create a system with a graphical interface allowing for 
viewing images from many IP cameras connected to one server using a web socket.

## User Interface 
![UI](https://github.com/MKaczmarski07/cctv/assets/95142305/209b75c1-5b6f-4691-91f8-5610cc9eae69)


## How does it work?

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


