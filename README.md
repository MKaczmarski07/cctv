# CCTV Control Panel
<i>Project done for the subject audio-video streaming </i> <br/>

## About
The main idea was to create a system with a graphical interface allowing for 
viewing images from many IP cameras connected to one server using a web socket.

## User Interface 

## Key Features

### Server
- Handling multiple connections using multithreading.
- Receiving and decoding video data.
- Displayig multiple videos in form of grid inside a graphical interface.
- Displaying network related data and current number of connected clients.

### Client
- Live video streaming

## Technology Stack

[Python 🔗](https://www.python.org)<br>
[Customtkinter🔗](https://github.com/TomSchimansky/CustomTkinter)<br>
[OpenCV🔗](https://opencv.org)<br>
[imutils🔗](https://pypi.org/project/imutils/)<br>
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
    pip install imutils
    pip install pillow

To run server or client script from the command line, in the app workspace type:

    python scriptName.py 


