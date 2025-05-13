# IMX219対応手順

## H/Wの注意事項
Renesas EVK（https://www.renesas.com/ja/products/microcontrollers-microprocessors/rz-mpus/rzv2h-evk-rzv2h-quad-core-vision-ai-mpu-evaluation-kit）に
準じたMIPI-CSI2の22ピンI/Fのカメラの場合は、反転FPC（電極面が同一面のもの）を用いて接続してください。
Raspberry Piに準じたカメラのFPC（電極面が反転面のもの）はそのまま接続しても問題ありません。

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
    以下のカーネルコンフィグを有効化（"y"に設定）してください。
    - CONFIG_VIDEO_IMX219

2. カーネルイメージをビルドする。
    ```
    # make -j4 Image
    ```
    ビルド成果物は以下です。
    - ./arch/arm64/boot/Image

3. デバイスツリーをビルドする。
    ```
    # make -j4 renesas/overlays/kakip-es1-imx219-overlay.dtb
    ```
    ビルド成果物は以下です。
    - ./arch/arm64/boot/dts/renesas/overlays/kakip-es1-imx219-overlay.dtb

4. ビルド後はexitでコンテナから抜ける。
    ```
    # exit
    ```

#### カーネルの更新手順

#### カーネルイメージとdtbファイルの配置
1. SDカードをPCにマウントする。

    /mntに手動でマウントする場合の手順です。  
    自動マウントされる環境の場合は、以降マウント先のパスを読み替えてください。

    ```
    # sd<X>は環境によります。
    $ sudo mount /dev/sd<X>2 /mnt
    ```

2. ビルドしたカーネルイメージを更新する。

    ```
    $ sudo cp ./arch/arm64/boot/Image /mnt/boot/Image-5.10.145-cip17-yocto-standard
    ```

3. ビルドしたdtbファイルをdtboファイルとして配置する。
    ```
    $ sudo cp ./arch/arm64/boot/dts/renesas/overlays/kakip-es1-imx219-overlay.dtb /mnt/boot/kakip-es1-imx219.dtbo
    ```

#### kakipでのdtboファイルの適用
1. カーネルイメージとdtbファイルを更新したSDカードでkakipを起動する。

2. kakipで以下のコマンドを実行する。
    ```
    $ sudo fw_setenv boot_fdt_overlay yes
    $ sudo fw_setenv fdt_overlay_files kakip-es1-imx219
    ```

3. kakipを再起動する。
    ```
    $ sudo shutdown -r now
    ```

### セルフコンパイル
#### 事前準備
1. 依存パッケージのインストールを行う。
    ```
    $ sudo apt update
    $ sudo apt install -y git flex bison bc build-essential libncurses-dev pkg-config gcc-9
    ```

    ※ RZ/V2H用AI SDKのコンテナイメージに合わせて`gcc-9`を使用します。

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
    以下のカーネルコンフィグを有効化（"y"に設定）してください。
    - CONFIG_VIDEO_ECAM_IMX462

2. カーネルイメージをビルドする。
    ```
    $ make -j4 Image CC=gcc-9
    ```
    ビルド成果物は以下です。
    - ./arch/arm64/boot/Image

3. デバイスツリーをビルドする。
    ```
    $ make -j4 renesas/overlays/kakip-es1-imx219-overlay.dtb CC=gcc-9
    ```
    ビルド成果物は以下です。
    - ./arch/arm64/boot/dts/renesas/overlays/kakip-es1-imx219-overlay.dtb

#### カーネルの更新手順
1. ビルドしたカーネルイメージを更新する。

    ```
    $ sudo cp ./arch/arm64/boot/Image /boot/Image-5.10.145-cip17-yocto-standard
    ```

2. ビルドしたdtbファイルをdtboファイルとして配置する。
    ```
    $ sudo cp ./arch/arm64/boot/dts/renesas/overlays/kakip-es1-imx219-overlay.dtb /boot/kakip-es1-imx219.dtbo
    ```

3. 以下のコマンドを実行する。
    ```
    $ sudo fw_setenv boot_fdt_overlay yes
    $ sudo fw_setenv fdt_overlay_files kakip-es1-imx219
    ```

4. kakipを再起動する。
    ```
    $ sudo shutdown -r now
    ```

## 映像取得手順

### 注意事項

1. UDL（ディスプレイリンク）で接続したディスプレイにログインした状態で行ってください。

### 接続構成

KakipとIMX219は以下のように接続してください。
#### 全体
<img src="./image/image-0.jpg" width="50%">

#### Kakip側の接続
<img src="./image/image-1.jpg" width="50%">
<img src="./image/image-2.jpg" width="50%">

#### IMX219側の接続
<img src="./image/image-3.jpg" width="50%">
<img src="./image/image-4.jpg" width="50%">

### 事前準備

1. ビデオパイプラインを設定する。

    ```
    $ media-ctl -d /dev/media<X> -r
    $ media-ctl -d /dev/media<X> -V "'imx219 <X>-0010':0 [fmt:SRGGB8_1X8/640x480 field:none]"
    $ media-ctl -d /dev/media<X> -V "'rzg2l_csi2 160<X>0400.csi2<X>':1 [fmt:SRGGB8_1X8/640x480 field:none]"
    $ media-ctl -d /dev/media<X> -l "'rzg2l_csi2 160<X>0400.csi2<X>':1 -> 'CRU output':0 [1]"
    ```

    ※\<X>の箇所は、接続したCSI端子に応じて変更してください。CAM0端子なら`0`、CAM1端子なら`1`となります。
    ※例えば、CAM0端子の場合は以下になります。
    ```
    $ media-ctl -d /dev/media0 -r
    $ media-ctl -d /dev/media0 -V "'imx219 0-0010':0 [fmt:SRGGB8_1X8/640x480 field:none]"
    $ media-ctl -d /dev/media0 -V "'rzg2l_csi2 16000400.csi20':1 [fmt:SRGGB8_1X8/640x480 field:none]"
    $ media-ctl -d /dev/media0 -l "'rzg2l_csi2 16000400.csi20':1 -> 'CRU output':0 [1]"
    ```

2. 取得映像の明るさを調整する。
    
    ```
    $ v4l2-ctl --set-ctrl=digital_gain=1000
    $ v4l2-ctl --set-ctrl=analogue_gain=100
    ```

### 映像取得手順

1. IMX219から映像を取得し、ディスプレイに表示する。

    ```
    $ gst-launch-1.0 v4l2src device=/dev/video0 ! video/x-bayer,format=bggr,width=640,height=480,framerate=30/1 ! bayer2rgb ! autovideosink sync=false
    ```
