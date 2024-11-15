# SimpliFRy

![Project Logo](static/favicon.png)

---

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)

---

## Description

**SimpliFRy** is the core component of [Real-time FRS 2.0](https://github.com/CJBuzz/Real-time-FRS-2.0) and is the software that handles Real-time Facial Recognition. It is a locally-hosted web application built using python 3.10 and [Flask](https://github.com/pallets/flask), and makes use of the [insightface](https://github.com/deepinsight/insightface) library by deepinsight for face detection and generation of embeddings as well as the [voyager](https://github.com/spotify/voyager) library by Spotify for K-Nearest Neighbour search.

If you are a developer and would like to understand more about how simpliFRy works, refer to the [Developer Guide](Developer%20Guide.md)

---

## Features

### Cutting out the need for 3rd Party Softwares.

Previous iterations of Fusion's Facial Recognition System reads the live video feed through _Video Capture Devices_. These include Webcams, USB Capture Devices and OBS Virtual Camera. However, most of the cameras used in conjunction with the FRS transmit their feed via _Real-Time Streaming Protocol_ (RTSP) through ethernet cables. To access the feed, 3rd party softwares such as OBS Studio and VLC Media Player are used to broadcast the RTSP stream in a Virtual Camera.

As OBS Studio only broadcasts one instance of virtual camera at a time, this limits the number of camera feed a computer, no matter how computationally powerful, can access to one. As a result, multiple computers have to be used whenever multiple cameras are used, which they often are (in a bid to cover more angles for facial recognition).

The use of **FFmpeg** in simpliFRy to read the the RTSP stream directly solves this issue by bypassing the need for OBS Studio. Now, a sufficiently powerful computer is able to simultaneously run facial recognition on at least 2 video feeds at once (subject to quality of ethernet cable), maximising the use of hardware resources.

Incidentally, removing the need for 3rd party softwares, not only simplifies the installation process (as you only need to install this software), but also reduces the complexity of operating the program, hence making it easier even for non-technologically inclined persons to learn and remember.

### [Enhanced Detection Algorithm](Developer%20Guide.md#enhanced-detection-algorithm)

### [Microservice Design](Developer%20Guide.md#microservice-design)

---

## Installation

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Nvidia Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) (for GPU usage within docker container, which is very recommended; install via WSL)

### Installation via Docker

1. Clone the repository:

   ```bash
   git clone https://github.com/CJBuzz/Real-time-FRS-2.0.git
   ```

2. Navigate to simpliFRy directory

   ```bash
   cd simpliFRy
   ```

3. Build Docker Image
   ```bash
   docker compose build
   ```

### Installation by other means

It is highly recommended to install and run simpliFRy via Docker, else there is a need to install dependencies such as CUDA and cuDNN separately. It is quite troublesome to achieve version compatibility for CUDA, cuDNN, pyTorch and onnxruntime. However, if you insist on refusing to use Docker, below are the versions that worked for me.

- CUDA 11.8
- cuDNN 8.9.2.26
- pyTorch 2.1.2+cu118
- onnxruntime 1.18.1

In addition, if you are using windows, there is a need to install CMake and Microsoft Visual Studio C++ built tools separately.

Afterwards, you can create a virtual environment in the `simpliFRy` directory

```bash
py -m venv venv
```

Activate it

```bash
venv\Scripts\activate # on windows, use source venv/bin/activate for linux and macOS
```

Install the requirements with pip

```bash
pip install -r requirements.txt
```

---

## Usage

### Docker

1. Start Docker Desktop application

2. Run the container

If you wish to create a new container, run the following command

```bash
docker run -p 1333:1333 -v "/absolute/path/to/simplifry/data:/app/data" --gpus all simplifry-simplifry
```

Alternatively, you can run docker compose from the `simpliFRy` directory

```bash
docker compose up --no-build
```

Access the web UI at <http://127.0.0.1:1333> (preferably using Microsoft Edge)

The port argument `1333:1333` can be changed according to what you require, if you want to run at port 2000 instead, use `2000:1333` instead.

If you want to run multiple containers, run one container at with the port argument `1333:1333` (port 1333) and another with the argument `2000:1333` (this means port 2000, you can use another port number).

This means the 2nd container can be accessed at <http://127.0.0.1:2000>.

Alternatively, you can edit `docker-compose.yml` and run

```bash
docker compose up --no-build
```

If you do have an existing container, you can start it from the Docker Desktop application

### Without Docker (not recommended)

Run the `app.py` script in the simpliFRy virtual environment

```bash
py app.py
```

### Data Preparation

To conduct facial recognition, you need to load images of people you wish to be recognised into simpliFRy. Each person can have 1 or more pictures.

1. From the `simpliFRy/data` folder (created automatically when starting the app), create a folder called `faces`.

2. Place all the images of people you wish to be detected within the `faces` folder.

3. In the `simpliFRy/data` folder, create a JSON file that maps the image file name with the name of the person to be recognised (you can call it anything, such as `personnel.json`). Format it like below.

```json
{
  "img_folder_path": "path/to/image/folder",
  "details": [
    {
      "name": "Person One",
      "images": ["image1.jpg", "image2.png"]
    },
    {
      "name": "Person Two",
      "images": ["image3.jpg", "image4.png"]
    }
    // Other similar entries as above
  ]
}
```

`img_folder_path` will the path to the folder with all the faces **relative to `data`** (it need not be called `faces`).


For example, if `john_doe1.jpg` and `john_doe2.png` are pictures of 'John Doe' while `jane_smith.png` is a picture of 'Jane Smith', and all images are in a folder called `pictures`, this is the directory structure. 

```
simpliFRy/
├── data/
|   ├── logs/
|   ├── pictures/
|   |   ├── john_doe1.jpg
|   |   ├── john_doe2.png
|   |   └── jane_smith.png
|   └── personnel.json
└── other files and folders
```

`personnel.json` would look like this

```json
{
  "img_folder_path": "pictures",
  "details": [
    {
      "name": "John Doe",
      "images": ["john_doe1.jpg", "john_doe2.png"]
    },
    {
      "name": "Jane Smith",
      "images": ["jane_smith.png"]
    }
  ]
}
```

**Importantly, the folder contains the images (e.g. `pictures` in the example above), and the JSON file that maps names to images (e.g. `personnel.json`) need not have a fixed name, as long as they are located within the `data` folder (which needs to be exactly called `data`).**

#### Data Folder

The `data` folder in `simpliFRy` is a **volume mount** as it is volume mounted to the `/app/data` directory within the docker container. Hence, it is the primary way to pass information to (e.g. folder of images, refer to [Data Preparation](#data-preparation) for more info) and from (logs) the container.

Directory structure

```
simpliFRy/
├── data/
|   ├── logs/
|   |   ├── Logs YY-MM-DD hh-mm-ss.logs
|   ├── pictures/
|   |   ├── john_doe1.jpg
|   |   ├── john_doe2.png
|   |   └── jane_smith.png
|   └── personnel.json
└── other files and folders
```

Everytime the app is started, a new `.logs` file will be created. It will list key actions undertaken by the simpliFRy app in that session.

### Software

The app is hosted on `0.0.0.0`. Thus it is accessible by other computers in the same local area network using the network IP address of the hosting device.

Running on port `1333`, the main web page is accessible when going the the URL <http://127.0.0.1:1333> on the browser (Microsoft Edge recommended). 

![simpliFRy main page](assets/main_page.png)

1. Fill in the **Video Stream Source** input with the URL to the RTSP stream. The format for RTSP URLs is `rtsp://[<username>:<password>@]<ip_address>:<rtsp_port>/[<endpoint>]`.

  - Enclosed in angle brackets: variables to be replaced accordingly
  - Enclosed in square brackets: optional

Example RTSP URL `rtsp://admin:password123@192.168.1.42:4242/stream`

2. Fill in the **Path to JSON file** input with the path the the JSON file that maps image file names to names of people to be recognised. The path <ins>must be relative to the `data` folder</ins>.

**The JSON file need only be filled in the first time or whenever you would like to update the pictures or names, it can be left blank otherwise**

3. Click on the 'Submit' button and wait a few seconds. The web page will then show the video stream (from the RTSP URL) with labelled bounding boxes drawn on it.

### Settings

To adjust parameters used in the FR algorithm, go to <http://127.0.0.1:1333/settings>.

![simpliFRy settings page](assets/settings_page.png)

For more information on the parameters, click [here](Developer%20Guide.md#fr-settings).
