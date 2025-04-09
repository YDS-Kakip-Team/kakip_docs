# Kakip X1301 HDMI to CSI-2 Shield対応手順

## 接続方法

[公式のハードウェアマニュアル](https://suptronics.com/Raspberrypi/Interface/x1301-v1.1_hardware.html)と同様に接続する。

## 事前準備

1. EDID.txtファイルを作成する。
    ```
    $ vi 1080P60EDID.txt
    ```

    以下のEDIDデータを1080P60EDID.txtにコピーする。
    ```
    00ffffffffffff005262888800888888
    1c150103800000780aEE91A3544C9926
    0F505400000001010101010101010101
    010101010101011d007251d01e206e28
    5500c48e2100001e8c0ad08a20e02d10
    103e9600138e2100001e000000fc0054
    6f73686962612d4832430a20000000FD
    003b3d0f2e0f1e0a202020202020014f
    020322444f841303021211012021223c
    3d3e101f2309070766030c00300080E3
    007F8c0ad08a20e02d10103e9600c48e
    210000188c0ad08a20e02d10103e9600
    138e210000188c0aa01451f01600267c
    4300138e210000980000000000000000
    00000000000000000000000000000000
    00000000000000000000000000000015
    ```

2. EDIDデータを読み込む。

    ```
    $ v4l2-ctl -d /dev/v4l-subdev1 --set-edid=file=./1080P60EDID.txt --fix-edid-checksums
    ```

3. HDMI出力側機器をX1301に接続する。

4. 現在のHDMI入力信号情報を確認する。

    ```
    $ v4l2-ctl -d /dev/v4l-subdev2 --query-dv-timings
        Active width: 1920
        Active height: 1080
        Total width: 2200
        Total height: 1125
        Frame format: progressive
        Polarities: -vsync -hsync
        Pixelclock: 148500000 Hz (60.00 frames per second)
        Horizontal frontporch: 0
        Horizontal sync: 280
        Horizontal backporch: 0
        Vertical frontporch: 0
        Vertical sync: 45
        Vertical backporch: 0
        Standards:
        Flags:
    ```
    ※ 上記のように正しい解像度1080p60Hzを取得できない場合は、HDMI出力側機器の解像度が1080p60Hzに設定されているか確認すること。

5. キャプチャ設定にスクリーンタイミングを適用する。

    ```
    $ v4l2-ctl -d /dev/v4l-subdev1 --set-dv-bt-timings query
    ```

6. メディアノードを設定する。

    ```
    $ media-ctl -d /dev/media<X> -r
    $ media-ctl -d /dev/media<X> -l "'rzg2l_csi2 160<X>0400.csi2<X>':1 -> 'CRU output':0 [1]"
    $ media-ctl -d /dev/media<X> -V "'rzg2l_csi2 160<X>0400.csi2<X>':0 [fmt:RGB888_1X24/1920x1080 $ field:none colorspace:srgb]"
    $ media-ctl -d /dev/media<X> -V "'rzg2l_csi2 160<X>0400.csi2<X>':1 [fmt:RGB888_1X24/1920x1080 field:none colorspace:srgb]"
    $ media-ctl -d /dev/media<X> -V "'tc358743 <X>-000f':0 [fmt:RGB888_1X24/1920x1080 field:none colorspace:srgb]"
    ```

    ※\<X>の箇所は、接続したCSI端子に応じて変更すること。CAM0端子なら`0`、CAM1端子なら`1`。
    ※例えば、CAM0端子の場合は以下になる。

    ```
    $ media-ctl -d /dev/media0 -r
    $ media-ctl -d /dev/media0 -l "'rzg2l_csi2 16000400.csi20':1 -> 'CRU output':0 [1]"
    $ media-ctl -d /dev/media0 -V "'rzg2l_csi2 16000400.csi20':0 [fmt:RGB888_1X24/1920x1080 field:none colorspace:srgb]"
    $ media-ctl -d /dev/media0 -V "'rzg2l_csi2 16000400.csi20':1 [fmt:RGB888_1X24/1920x1080 field:none colorspace:srgb]"
    $ media-ctl -d /dev/media0 -V "'tc358743 0-000f':0 [fmt:RGB888_1X24/1920x1080 field:none colorspace:srgb]"
    ```

## 映像取得手順

### v4l2-ctlで取得する場合（[公式手順](https://suptronics.com/Raspberrypi/Interface/x1301-v1.1_software.html)）
- フレームの取得コマンド 
    ```
    $ v4l2-ctl --verbose -d /dev/video0 --set-fmt-video=width=1920,height=1080,pixelformat='BGR3' --stream-mmap=4 --stream-skip=3 --stream-count=2 --stream-to=csitest.yuv --stream-poll
    ```

    実行後、以下のファイルが作成される。
    - ./csitest.yuv

- 取得したフレームの表示コマンド
    ```
    $ sudo apt update
    $ sudo apt install ffmpeg
    $ ffplay -f rawvideo -video_size 1920x1080 -pixel_format bgr24 csitest.yuv
    ```

### gstreamerで取得する場合
- 映像の取得コマンド

    ```
    $ gst-launch-1.0 -e -v v4l2src device=/dev/video0 ! video/x-raw,height=1080,width=1920,format=BGR,framerate=60/1 ! autovideosink sync=false
    ```
 