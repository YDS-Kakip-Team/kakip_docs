#!/usr/bin/env python3

import gi
import cv2
import numpy as np
from threading import Lock, Thread
import time
import sys
import subprocess
import argparse
import os
import re
import psutil

gi.require_version('Gst', '1.0')
from gi.repository import Gst

CAMERA_CONFIGS = {
    0: {'media_dev': '/dev/media0', 'subdev': '/dev/v4l-subdev1', 'csi_dev': 'rzg2l_csi2 16000400.csi20',
        'sensor': 'imx219 0-0010', 'active_pad': 2, 'csi_port': 'CSI20'},
    1: {'media_dev': '/dev/media1', 'subdev': '/dev/v4l-subdev3', 'csi_dev': 'rzg2l_csi2 16010400.csi21',
        'sensor': 'imx219 1-0010', 'active_pad': 2, 'csi_port': 'CSI21'},
    2: {'media_dev': '/dev/media2', 'subdev': '/dev/v4l-subdev4', 'csi_dev': 'rzg2l_csi2 16020400.csi22',
        'sensor': 'imx219 2-0010', 'active_pad': 2, 'csi_port': 'CSI22'},
    3: {'media_dev': '/dev/media3', 'subdev': '/dev/v4l-subdev5', 'csi_dev': 'rzg2l_csi2 16030400.csi23',
        'sensor': 'imx219 3-0010', 'active_pad': 2, 'csi_port': 'CSI23'}
}

DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 480
DEFAULT_FRAMERATE = '30/1'
DEFAULT_ANALOGUE_GAIN = 232
DEFAULT_DIGITAL_GAIN = 400
DEFAULT_EXPOSURE = 400

BAYER_FORMAT = {'gst': 'rggb', 'cv': cv2.COLOR_BAYER_RG2RGB, 'media': 'SRGGB8_1X8'}

RED_GAIN = 1.4
GREEN_GAIN = 1.0
BLUE_GAIN = 1.4

GST_QUEUE_BUFFERS = 2

def get_screen_resolution():
    try:
        import tkinter
        root = tkinter.Tk()
        root.withdraw()
        width, height = root.winfo_screenwidth(), root.winfo_screenheight()
        root.destroy()
        return width, height
    except:
        return 1920, 1080

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Kakip Software Isp for Four IMX219 Cameras',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('resolution', nargs='?', default=f'{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}',
                       help=f'Resolution WIDTHxHEIGHT (default: {DEFAULT_WIDTH}x{DEFAULT_HEIGHT})')

    parser.add_argument('-c', '--cameras', default='0,1,2,3',
                       help='Comma-separated camera indices (0-3, default: 0,1,2,3)')

    parser.add_argument('-a', '--analogue-gain', type=int, default=DEFAULT_ANALOGUE_GAIN,
                       help=f'Analogue gain (range: 0-232, default: {DEFAULT_ANALOGUE_GAIN})')

    parser.add_argument('-d', '--digital-gain', type=int, default=DEFAULT_DIGITAL_GAIN,
                       help=f'Digital gain (range: 256-4095, default: {DEFAULT_DIGITAL_GAIN})')

    parser.add_argument('-e', '--exposure', type=int, default=DEFAULT_EXPOSURE,
                       help=f'Exposure time (range: 4-1759, default: {DEFAULT_EXPOSURE})')

    parser.add_argument('-p', '--performance-monitor', action='store_true',
                       help='Enable CPU and FPS monitoring')

    args = parser.parse_args()

    try:
        width, height = map(int, args.resolution.split('x'))
    except ValueError:
        parser.error(f"Invalid resolution format: '{args.resolution}'. Use WIDTHxHEIGHT format (e.g., 1920x1080)")

    try:
        camera_indices = [int(x.strip()) for x in args.cameras.split(',')]
        for idx in camera_indices:
            if idx not in CAMERA_CONFIGS:
                parser.error(f"Invalid camera index: {idx}. Valid indices are 0-3")
    except ValueError:
        parser.error(f"Invalid camera list: '{args.cameras}'. Use comma-separated indices (e.g., 0,1,2)")

    if not 0 <= args.analogue_gain <= 232:
        parser.error(f"Analogue gain {args.analogue_gain} out of range (0-232)")

    if not 256 <= args.digital_gain <= 4095:
        parser.error(f"Digital gain {args.digital_gain} out of range (256-4095)")

    if not 4 <= args.exposure <= 1759:
        parser.error(f"Exposure {args.exposure} out of range (4-1759)")

    return (width, height, camera_indices, args.analogue_gain,
            args.digital_gain, args.exposure, args.performance_monitor)

def detect_and_map_cameras():
    mapped_indices = []
    print("Detecting and mapping cameras...")

    for idx, config in CAMERA_CONFIGS.items():
        media_dev = config['media_dev']

        if not os.path.exists(media_dev):
            print(f"Camera {idx} device not found")
            continue

        result = subprocess.run(['media-ctl', '-d', media_dev, '-p'],
                              capture_output=True, text=True)

        if result.returncode == 0 and 'imx219' in result.stdout:
            match = re.search(r'device node name (/dev/video\d+)', result.stdout)
            if match:
                video_node = match.group(1)
                CAMERA_CONFIGS[idx]['video_dev'] = video_node
                mapped_indices.append(idx)
                print(f"Camera {idx} ({media_dev}) -> {video_node}")

    return mapped_indices

def setup_camera_controls(camera_idx, analogue_gain, digital_gain, exposure):
    config = CAMERA_CONFIGS[camera_idx]
    subdev = config['subdev']
    print(f"Configuring camera {camera_idx} controls...")

    controls = f'analogue_gain={analogue_gain},digital_gain={digital_gain},exposure={exposure}'
    subprocess.run(['v4l2-ctl', '-d', subdev, '--set-ctrl', controls])
    print(f"Camera {camera_idx} controls configured")

def setup_media_ctl(camera_idx, width, height):
    config = CAMERA_CONFIGS[camera_idx]
    format_str = f"{BAYER_FORMAT['media']}/{width}x{height}"
    print(f"Configuring camera {camera_idx} media-ctl...")

    commands = [
        f'media-ctl -d {config["media_dev"]} -r',
        f'media-ctl -d {config["media_dev"]} -V \'"{config["sensor"]}":0[fmt:{format_str} field:none]\'',
        f'media-ctl -d {config["media_dev"]} -V \'"{config["csi_dev"]}":{config["active_pad"]}[fmt:{format_str} field:none]\'',
        f'media-ctl -d {config["media_dev"]} -l \'"{config["csi_dev"]}":{config["active_pad"]} -> "CRU output":0[1]\''
    ]

    for cmd in commands:
        subprocess.run(cmd, shell=True)

    print(f"Camera {camera_idx} media-ctl configured")

def create_wb_lookup_tables():
    lut_range = np.arange(256, dtype=np.float32)
    r_lut = np.clip(lut_range * RED_GAIN, 0, 255).astype(np.uint8)
    g_lut = np.clip(lut_range * GREEN_GAIN, 0, 255).astype(np.uint8)
    b_lut = np.clip(lut_range * BLUE_GAIN, 0, 255).astype(np.uint8)
    return r_lut, g_lut, b_lut

class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.process = psutil.Process(os.getpid())
        self.cpu_samples = []
        self.fps_samples = {}
        self.lock = Lock()
        self.process.cpu_percent(interval=None)

    def sample_cpu(self):
        with self.lock:
            self.cpu_samples.append(self.process.cpu_percent(interval=None))

    def record_fps(self, camera_idx, fps):
        with self.lock:
            if camera_idx not in self.fps_samples:
                self.fps_samples[camera_idx] = []
            self.fps_samples[camera_idx].append(fps)

    def get_statistics(self):
        with self.lock:
            cpu_copy = self.cpu_samples.copy()
            fps_copy = {k: v.copy() for k, v in self.fps_samples.items()}

        runtime = time.time() - self.start_time
        stats = {
            'runtime': runtime,
            'cpu': {
                'avg': np.mean(cpu_copy) if cpu_copy else 0,
                'max': np.max(cpu_copy) if cpu_copy else 0,
                'min': np.min(cpu_copy) if cpu_copy else 0
            },
            'fps': {}
        }

        for cam_idx, fps_list in fps_copy.items():
            if fps_list:
                stats['fps'][cam_idx] = {
                    'avg': np.mean(fps_list),
                    'max': np.max(fps_list),
                    'min': np.min(fps_list)
                }

        return stats

    def print_statistics(self):
        stats = self.get_statistics()
        print("\n" + "="*60)
        print("PERFORMANCE STATISTICS")
        print("="*60)
        print(f"Runtime: {stats['runtime']:.2f} seconds")
        print(f"\nCPU Usage:")
        print(f"  Average: {stats['cpu']['avg']:.2f}%")
        print(f"  Maximum: {stats['cpu']['max']:.2f}%")
        print(f"  Minimum: {stats['cpu']['min']:.2f}%")
        print(f"\nFPS Statistics:")
        for cam_idx, fps_stats in stats['fps'].items():
            print(f"  Camera {cam_idx}:")
            print(f"    Average: {fps_stats['avg']:.2f} fps")
            print(f"    Maximum: {fps_stats['max']:.2f} fps")
            print(f"    Minimum: {fps_stats['min']:.2f} fps")
        print("="*60)

class SingleCameraBridge:
    def __init__(self, camera_idx, width, height, perf_monitor=None):
        self.camera_idx = camera_idx
        self.width = width
        self.height = height
        self.framerate = DEFAULT_FRAMERATE
        self.perf_monitor = perf_monitor
        self.config = CAMERA_CONFIGS[camera_idx]

        self.r_lut, self.g_lut, self.b_lut = create_wb_lookup_tables()
        self.rgb_buffer = np.empty((height, width, 3), dtype=np.uint8)
        self.latest_frame = None
        self.frame_lock = Lock()

        self.frame_count = 0
        self.last_fps_time = time.time()
        self.current_fps = 0.0

        self._init_pipeline()

    def _init_pipeline(self):
        pipeline_str = (
            f"v4l2src device={self.config['video_dev']} ! "
            f"video/x-bayer,format={BAYER_FORMAT['gst']},width={self.width},"
            f"height={self.height},framerate={self.framerate} ! "
            f"queue max-size-buffers={GST_QUEUE_BUFFERS} leaky=downstream ! "
            f"appsink name=sink emit-signals=True max-buffers={GST_QUEUE_BUFFERS} drop=True sync=false"
        )

        self.pipeline = Gst.parse_launch(pipeline_str)
        self.appsink = self.pipeline.get_by_name('sink')
        self.appsink.connect('new-sample', self.on_new_sample)

    def process_frame(self, raw_data):
        if len(raw_data) != self.height * self.width:
            return None

        bayer_8bit = np.frombuffer(raw_data, dtype=np.uint8).reshape(self.height, self.width)
        cv2.cvtColor(bayer_8bit, BAYER_FORMAT['cv'], dst=self.rgb_buffer)

        b, g, r = cv2.split(self.rgb_buffer)
        r = cv2.LUT(r, self.r_lut)
        g = cv2.LUT(g, self.g_lut)
        b = cv2.LUT(b, self.b_lut)

        return cv2.merge((b, g, r))

    def on_new_sample(self, sink):
        sample = sink.emit('pull-sample')
        if not sample:
            return Gst.FlowReturn.OK

        buf = sample.get_buffer()
        success, map_info = buf.map(Gst.MapFlags.READ)

        if success:
            processed_frame = self.process_frame(map_info.data)
            if processed_frame is not None:
                with self.frame_lock:
                    self.latest_frame = processed_frame
                self.update_fps_counter()
            buf.unmap(map_info)

        return Gst.FlowReturn.OK

    def update_fps_counter(self):
        self.frame_count += 1
        current_time = time.time()

        if current_time - self.last_fps_time >= 5.0:
            elapsed = current_time - self.last_fps_time
            self.current_fps = self.frame_count / elapsed

            if self.perf_monitor:
                self.perf_monitor.record_fps(self.camera_idx, self.current_fps)

            print(f"Camera {self.camera_idx} FPS: {self.current_fps:.2f}")
            self.frame_count = 0
            self.last_fps_time = current_time

    def get_latest_frame(self):
        with self.frame_lock:
            return self.latest_frame.copy() if self.latest_frame is not None else None

    def start(self):
        self.pipeline.set_state(Gst.State.PLAYING)

    def stop(self):
        self.pipeline.set_state(Gst.State.NULL)

class MultiCameraManager:
    def __init__(self, camera_indices, width, height, perf_monitor=None):
        self.camera_indices = camera_indices
        self.width = width
        self.height = height
        self.perf_monitor = perf_monitor

        self.cameras = {
            idx: SingleCameraBridge(idx, width, height, perf_monitor)
            for idx in camera_indices
        }

        num_cameras = len(camera_indices)
        if num_cameras == 1:
            self.rows, self.cols = 1, 1
        elif num_cameras == 2:
            self.rows, self.cols = 1, 2
        else:
            self.rows, self.cols = 2, 2

        self.display_width = width * self.cols
        self.display_height = height * self.rows

        screen_width, screen_height = get_screen_resolution()

        self.is_scaling_needed = (
            self.display_width > screen_width * 0.95 or
            self.display_height > screen_height * 0.95
        )

        if self.is_scaling_needed:
            max_width = screen_width * 0.9
            max_height = screen_height * 0.9
            aspect_ratio = self.display_width / self.display_height

            scaled_width = max_width
            scaled_height = scaled_width / aspect_ratio

            if scaled_height > max_height:
                scaled_height = max_height
                scaled_width = scaled_height * aspect_ratio

            self.scaled_display_size = (int(scaled_width), int(scaled_height))
        else:
            self.scaled_display_size = (self.display_width, self.display_height)

        self.scaled_cell_width = self.scaled_display_size[0] // self.cols
        self.scaled_cell_height = self.scaled_display_size[1] // self.rows

        print(f"Multi-camera manager initialized for {num_cameras} cameras")
        print(f"Grid layout: {self.rows}x{self.cols}")
        print(f"Display size: {self.scaled_display_size[0]}x{self.scaled_display_size[1]}")

    def arrange_frames(self):
        frames = []

        for position in range(self.rows * self.cols):
            if position < len(self.camera_indices):
                camera_idx = self.camera_indices[position]
                frame = self.cameras[camera_idx].get_latest_frame()

                if frame is not None:
                    if self.is_scaling_needed:
                        frame = cv2.resize(frame,
                                         (self.scaled_cell_width, self.scaled_cell_height),
                                         interpolation=cv2.INTER_AREA)

                    cv2.putText(frame, f'Camera {camera_idx}', (10, 20),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    if self.perf_monitor:
                        fps_text = f'FPS: {self.cameras[camera_idx].current_fps:.1f}'
                        cv2.putText(frame, fps_text, (10, 40),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

                    frames.append(frame)
                else:
                    blank_frame = np.zeros((self.scaled_cell_height, self.scaled_cell_width, 3),
                                          dtype=np.uint8)
                    cv2.putText(blank_frame, f'Camera {camera_idx} (No Signal)', (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    frames.append(blank_frame)
            else:
                frames.append(np.zeros((self.scaled_cell_height, self.scaled_cell_width, 3),
                                      dtype=np.uint8))

        rows = []
        for row_idx in range(self.rows):
            start_idx = row_idx * self.cols
            end_idx = start_idx + self.cols
            rows.append(np.hstack(frames[start_idx:end_idx]))

        return np.vstack(rows)

    def start_all(self):
        print("Starting all cameras...")
        threads = [Thread(target=cam.start) for cam in self.cameras.values()]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        print("All cameras started")

    def stop_all(self):
        print("Stopping all cameras...")
        for camera in self.cameras.values():
            camera.stop()
        print("All cameras stopped")

    def display_loop(self):
        print("Starting display loop (press 'q' to quit)")
        window_name = 'Multi-Camera View'
        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

        cpu_sample_counter = 0

        while True:
            if self.perf_monitor and cpu_sample_counter % 30 == 0:
                self.perf_monitor.sample_cpu()
            cpu_sample_counter += 1

            display_frame = self.arrange_frames()

            if display_frame is not None:
                if self.perf_monitor:
                    stats = self.perf_monitor.get_statistics()
                    info_text = f"CPU: {stats['cpu']['avg']:.1f}%"
                    text_y = self.scaled_display_size[1] - 10
                    cv2.putText(display_frame, info_text, (10, text_y),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

                cv2.imshow(window_name, display_frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                time.sleep(0.01)

        cv2.destroyAllWindows()

def main():
    Gst.init(None)

    (width, height, requested_cameras, analogue_gain,
     digital_gain, exposure, enable_perf_monitor) = parse_arguments()

    available_cameras = detect_and_map_cameras()

    if not available_cameras:
        print("Error: No cameras detected")
        sys.exit(1)

    final_cameras = sorted([idx for idx in requested_cameras if idx in available_cameras])

    if not final_cameras:
        print("Error: None of the requested cameras are available")
        sys.exit(1)

    print(f"Using cameras: {final_cameras}")

    perf_monitor = PerformanceMonitor() if enable_perf_monitor else None

    for camera_idx in final_cameras:
        if 'video_dev' not in CAMERA_CONFIGS[camera_idx]:
            print(f"Warning: Camera {camera_idx} video device not mapped, skipping")
            continue

        print(f"\nConfiguring Camera {camera_idx}")
        setup_camera_controls(camera_idx, analogue_gain, digital_gain, exposure)
        setup_media_ctl(camera_idx, width, height)

    manager = MultiCameraManager(final_cameras, width, height, perf_monitor)

    manager.start_all()
    time.sleep(0.5)

    try:
        manager.display_loop()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        manager.stop_all()
        if perf_monitor:
            perf_monitor.print_statistics()

if __name__ == '__main__':
    main()
