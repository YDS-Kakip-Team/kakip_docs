# Kakip X1301 HDMI to CSI-2 Shield使用手順

## ビルド手順

### クロスコンパイル

#### 前提条件

[Renesas社の手順](https://renesas-rz.github.io/rzv_ai_sdk/5.00/getting_started.html)を参考にRZ/V2H用AI SDKのコンテナイメージを作成してください。

#### 事前準備
1. kakipのカーネルソースのリポジトリのクローンを行う。
    ```
    $ git clone https://github.com/YDS-Kakip-Team/kakip_linux.git
    ```

2. カーネルコンフィグを設定する。
    ```
    $ cd ./kakip_linux
    $ cp ./arch/arm64/configs/kakip.config ./.config
    ```

3. ビルド環境(コンテナ)を起動する。
    ```
    $ sudo docker run --rm -it -v $PWD:/kakip_linux -w /kakip_linux rzv2h_ai_sdk_image
    ```

4. 環境変数の設定と依存パッケージのインストールを行う。
    ```
    # source /opt/poky/3.1.31/environment-setup-aarch64-poky-linux
    # export PKG_CONFIG_DIR=/opt/poky/3.1.31/sysroots/aarch64-poky-linux/usr/lib64/pkgconfig
    # export PKG_CONFIG_LIBDIR=/opt/poky/3.1.31/sysroots/aarch64-poky-linux/usr/lib64/pkgconfig
    # export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/opt/poky/3.1.31/sysroots//aarch64-poky-linux/usr/share/pkgconfig
    # unset PKG_CONFIG_SYSROOT_DIR
    # apt update && apt install -y flex bison bc libssl-dev
    ```

#### ビルド手順
1. 必要なカーネルコンフィグを有効化する。
    ```
    # cd /kakip_linux
    # make menuconfig
    ```
    以下のカーネルコンフィグを有効化（"y"に設定）すること。
    - CONFIG_VIDEO_TC358743

2. カーネルイメージをビルドする。
    ```
    # make -j4 Image
    ```
    ビルド成果物は以下です。
    - ./arch/arm64/boot/Image

3. デバイスツリーをビルドする。
    ```
    # make -j4 renesas/overlays/kakip-es1-tc358743-overlay.dtb
    ```
    ビルド成果物は以下。
    - ./arch/arm64/boot/dts/renesas/overlays/kakip-es1-tc358743-overlay.dtb

4. ビルド後はexitでコンテナから抜ける。
    ```
    # exit
    ```

#### カーネルの更新手順

#### カーネルイメージとdtbファイルの配置
1. SDカードをPCにマウントする。

    /mntに手動でマウントする場合の手順。  
    自動マウントされる環境の場合は、以降マウント先のパスを読み替えること。

    ```
    # sd<X>は環境による。
    $ sudo mount /dev/sd<X>2 /mnt
    ```

2. ビルドしたカーネルイメージを更新する。

    ```
    $ sudo cp ./arch/arm64/boot/Image /mnt/boot/Image-5.10.145-cip17-yocto-standard
    ```

3. ビルドしたdtbファイルをdtboファイルとして配置する。
    ```
    $ sudo cp ./arch/arm64/boot/dts/renesas/overlays/kakip-es1-tc358743-overlay.dtb /mnt/boot/kakip-es1-tc358743.dtbo
    ```

#### kakipでのdtboファイルの適用
1. カーネルイメージとdtboファイルを配置したSDカードでkakipを起動する。

2. kakipで以下のコマンドを実行する。
    ```
    $ sudo fw_setenv boot_fdt_overlay yes
    $ sudo fw_setenv fdt_overlay_files kakip-es1-tc358743
    ```

3. kakipを再起動する。
    ```
    $ sudo shutdown -r now
    ```

### セルフコンパイル
#### 事前準備
1. 依存パッケージをインストールする。
    ```
    $ sudo apt update
    $ sudo apt install -y git flex bison bc build-essential libncurses-dev pkg-config gcc-9
    ```

    ※ RZ/V2H用AI SDKのコンテナイメージに合わせて`gcc-9`を使用する。

2. kakipのカーネルソースのリポジトリのクローンを行う。
    ```
    $ git clone https://github.com/YDS-Kakip-Team/kakip_linux.git
    ```

3. カーネルコンフィグを設定する。
    ```
    $ cd ./kakip_linux
    $ cp ./arch/arm64/configs/kakip.config ./.config
    ```

#### ビルド手順
1. 必要なカーネルコンフィグを有効化する。
    ```
    $ make menuconfig
    ```
    以下のカーネルコンフィグを有効化（"y"に設定）すること。
    - CONFIG_VIDEO_TC358743

2. カーネルイメージをビルドする。
    ```
    $ make -j4 Image CC=gcc-9
    ```
    ビルド成果物は以下。
    - ./arch/arm64/boot/Image

3. デバイスツリーをビルドする。
    ```
    $ make -j4 renesas/overlays/kakip-es1-tc358743-overlay.dtb CC=gcc-9
    ```
    ビルド成果物は以下。
    - ./arch/arm64/boot/dts/renesas/overlays/kakip-es1-tc358743-overlay.dtb

#### カーネルの更新手順
1. ビルドしたカーネルイメージを更新する。
    ```
    $ sudo cp ./arch/arm64/boot/Image /boot/Image-5.10.145-cip17-yocto-standard
    ```

2. ビルドしたdtbファイルをdtboファイルとして配置する。
    ```
    $ sudo cp ./arch/arm64/boot/dts/renesas/overlays/kakip-es1-tc358743-overlay.dtb /boot/kakip-es1-tc358743.dtbo
    ```

3. 以下のコマンドを実行する。
    ```
    $ sudo fw_setenv boot_fdt_overlay yes
    $ sudo fw_setenv fdt_overlay_files kakip-es1-tc358743
    ```

4. kakipを再起動する。
    ```
    $ sudo shutdown -r now
    ```

## 映像取得手順

### 接続方法

[公式のハードウェアマニュアル](https://suptronics.com/Raspberrypi/Interface/x1301-v1.1_hardware.html)と同様に接続する。

### 事前準備

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

### 映像取得手順

#### v4l2-ctlで取得する場合（[公式手順](https://suptronics.com/Raspberrypi/Interface/x1301-v1.1_software.html)）
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

#### gstreamerで取得する場合
- 映像の取得コマンド

    ```
    $ gst-launch-1.0 -e -v v4l2src device=/dev/video0 ! video/x-raw,height=1080,width=1920,format=BGR,framerate=60/1 ! autovideosink sync=false
    ```
 