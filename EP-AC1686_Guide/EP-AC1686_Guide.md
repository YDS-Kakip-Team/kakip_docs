# kakip EP-AC1686 対応手順

## 前提条件

[Renesas社の手順](https://renesas-rz.github.io/rzv_ai_sdk/5.00/getting_started.html)を参考にRZ/V2H用AI SDKのコンテナイメージを作成してください。

## クロスコンパイル

### 事前準備

1. 作業ディレクトリを作成する。
    ```
    mkdir kakip_work
    export WORK=$PWD/kakip_work
    ```
2. kakipのカーネルソースのリポジトリのクローンを行う。
    ```
    cd $WORK
    git clone https://github.com/YDS-Kakip-Team/kakip_linux.git
    ```

3. カーネルコンフィグを設定する。
    ```
    cp ./kakip_linux/arch/arm64/configs/kakip.config ./kakip_linux/.config
    ```

4. EP-AC1686ドライバ(rtl88x2bu)のソースコードを準備する。
    ```
    git clone https://github.com/RinCat/RTL88x2BU-Linux-Driver.git
    ```

5. ビルド環境(コンテナ)を起動する。
    ```
    cd $WORK
    sudo docker run --rm -it -v $PWD:/kakip_work -w /kakip_work rzv2h_ai_sdk_image
    ```

6. 環境変数の設定と依存パッケージのインストールを行う。
    ```
    source /opt/poky/3.1.31/environment-setup-aarch64-poky-linux
    export PKG_CONFIG_DIR=/opt/poky/3.1.31/sysroots/aarch64-poky-linux/usr/lib64/pkgconfig
    export PKG_CONFIG_LIBDIR=/opt/poky/3.1.31/sysroots/aarch64-poky-linux/usr/lib64/pkgconfig
    export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/opt/poky/3.1.31/sysroots//aarch64-poky-linux/usr/share/pkgconfig
    unset PKG_CONFIG_SYSROOT_DIR
    apt update && apt install -y flex bison bc libssl-dev
    ```

### ビルド手順

1. 必要なカーネルコンフィグを有効化する。
    ```
    cd /kakip_work/kakip_linux
    make menuconfig
    ```
    以下のカーネルコンフィグを有効化（"y"に設定）してください。
    - CONFIG_CFG80211

2. カーネルモジュールのビルドに必要なファイルをビルドする。
    ```
    cd /kakip_work/kakip_linux
    make -j4 modules_prepare
    ```

3. カーネルイメージをビルドする。
    ```
    make -j4 Image
    ```
    ビルド成果物は以下です。
    - ./arch/arm64/boot/Image

4. EP-AC1686ドライバ(rtl88x2bu)をビルドする。
    ```
    cd /kakip_work/RTL88x2BU-Linux-Driver
    make -j4 KSRC=/kakip_work/kakip_linux
    ```
    ビルド成果物は以下です。
    - ./88x2bu.ko

5. ビルド後はexitでコンテナから抜ける。
    ```
    exit
    ```

### インストール手順

Kakipのイメージが書き込まれているSDカードにドライバを配置します。
1. SDカードをPCにマウントする。

    /mntに手動でマウントする場合の手順です。  
    自動マウントされる環境の場合は、以降マウント先のパスを読み替えてください。

    ```
    # sd<X>は環境によります。
    sudo mount /dev/sd<X>2 /mnt
    ```

2. ビルドしたドライバとカーネルイメージを配置する。
    ```
    cd $WORK
    sudo cp ./RTL88x2BU-Linux-Driver/88x2bu.ko /mnt/lib/modules/5.10.145-cip17-yocto-standard/extra/
    sudo cp ./kakip_linux/arch/arm64/boot/Image /mnt/boot/Image-5.10.145-cip17-yocto-standard
    ```

3. SDカードをPCからアンマウントする。
    ```
    sudo umount /mnt
    ```

4. ドライバを配置したSDカードでkakipを起動する。

5. kakipで以下のコマンドを実行する。
    ```
    sudo depmod
    ```
