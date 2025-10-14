# Kakip Software ISP for IMX219 Cameras

A Python application for capturing and displaying video from up to four IMX219 cameras simultaneously on Kakip 8GB (Renesas RZ/V2H).

## Prerequisites

- Kakip 8GB (Renesas RZ/V2H) with OS image from Kakip official website <https://www.kakip.ai/>
- 1-4 IMX219 camera modules connected to CSI2 ports

## Installation

### 1. Download the Script

```bash
wget https://raw.githubusercontent.com/YDS-Kakip-Team/kakip_docs/main/IMX219_Software_ISP_Guide/kakip_soft_isp.py
```

### 2. Install Required Packages

```bash
sudo apt update
sudo apt install python3-opencv
sudo apt install python3-psutil
```
- python3-opencv version: 4.6.0+dfsg-13.1ubuntu1
- python3-psutil version: 5.9.8-2build2

## Usage

### Basic Syntax

```bash
python3 kakip_soft_isp.py [RESOLUTION] [OPTIONS]
```

### Command-Line Options

| Option | Description | Range | Default | Effect |
|--------|-------------|-------|---------|--------|
| `RESOLUTION` | Video resolution | 640x480, 1920x1080 | 640x480 | - |
| `-c, --cameras` | Camera indices | 0-3 | 0,1,2,3 | - |
| `-a, --analogue-gain` | Analogue gain | 0-232 | 232 | Higher value can get higher saturation |
| `-d, --digital-gain` | Digital gain | 256-4095 | 400 | Higher value can get higher saturation, but may also increase noise |
| `-e, --exposure` | Exposure gain | 4-1759 | 400 | Higher value can get brighter photo |
| `-p, --performance-monitor` | Enable CPU/FPS monitoring | - | Off | - |

### Examples

#### Display all 4 cameras at default resolution
```bash
python3 kakip_soft_isp.py
```

#### Display cameras 0 and 1 at 1920x1080
```bash
python3 kakip_soft_isp.py 1920x1080 -c 0,1
```

#### Single camera with performance monitoring
```bash
python3 kakip_soft_isp.py 1920x1080 -c 0 -p
```

#### Lower saturation
```bash
python3 kakip_soft_isp.py 640x480 -c 0,1,2,3 -d 256
```

#### Configuration optimized for low-light conditions
```bash
python3 kakip_soft_isp.py -e 1000
```

## Controls

- **Press 'q'**: Quit application
- **Ctrl+C**: Force shutdown
