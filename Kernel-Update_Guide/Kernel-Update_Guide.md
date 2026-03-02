# Kernel Update Guide

## Overview
After updating the Kakip kernel, it is necessary to rebuild and update the kernel modules.
This guide describes the build and deployment procedures for the following modules:
- mmngr_drv (for Mali GPU)
- udmabuf (for User-space DMA Buffer Driver)
- mali_km (for Mali GPU)
- uvcs_kernel_package (for User-space Video Codec Support)

## Build Procedures

### Cross-Compilation

#### Prerequisites

Please create a container image for the RZ/V2H AI SDK by referring to [Renesas' procedure](https://renesas-rz.github.io/rzv_ai_sdk/5.00/getting_started.html).

#### Preparation
1. Clone the kernel source repository.
    ```
    $ git clone https://github.com/YDS-Kakip-Team/kakip_linux.git
    ```

2. Set up the kernel configuration.
    ```
    $ cd ./kakip_linux
    $ cp ./arch/arm64/configs/kakip.config ./.config
    ```

3. Start the build environment (container).
    ```
    $ sudo docker run --rm -it -v $PWD:/kakip_linux -w /kakip_linux rzv2h_ai_sdk_image
    ```

4. Set up environment variables and install dependencies.
    ```
    # source /opt/poky/3.1.31/environment-setup-aarch64-poky-linux
    # export PKG_CONFIG_DIR=/opt/poky/3.1.31/sysroots/aarch64-poky-linux/usr/lib64/pkgconfig
    # export PKG_CONFIG_LIBDIR=/opt/poky/3.1.31/sysroots/aarch64-poky-linux/usr/lib64/pkgconfig
    # export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/opt/poky/3.1.31/sysroots//aarch64-poky-linux/usr/share/pkgconfig
    # unset PKG_CONFIG_SYSROOT_DIR
    # apt update && apt install -y flex bison bc libssl-dev
    ```

#### Building the Kernel Image

1. Build the kernel image.
    ```
    # cd ~/kakip_linux
    # make -j4
    ```
    Build artifacts:
    - ./arch/arm64/boot/Image
    - ./arch/arm64/boot/dts/renesas/kakip-es1.dtb

2. Build the kernel modules.
    ```
    # make modules_install INSTALL_MOD_STRIP=1 INSTALL_MOD_PATH=./modules/ -j4
    ```

#### Building Modules

After building the kernel, build the following modules in order.

##### 1. mmngr_drv

1. Clone the mmngr_drv repository.
    ```
    # git clone https://github.com/YDS-Kakip-Team/mmngr_drv.git

    For mmngr driver
    # cd mmngr_drv/mmngr_drv/mmngr/mmngr-module/files/mmngr/drv

    For mmngrbuf driver
    # cd mmngr_drv/mmngrbuf/mmngrbuf-module/files/mmngrbuf/drv
    ```

2. Build.
    ```
    # KDIR=~/kakip/kaki/kakip_linux  make
    # KDIR=~/kakip_linux INSTALL_MOD_PATH=~/kakip_linux/modules make modules_install
    ```

3. Verify the build artifact.
    - mmngr.ko
    - mmngrbuf.ko

##### 2. udmabuf

1. Clone the udmabuf repository.
    ```
    # git clone https://github.com/YDS-Kakip-Team/udmabuf.git
    # cd udmabuf
    ```

2. Build.
    ```
    # KDIR=~/kakip/kaki/kakip_linux  make
    # KDIR=~/kakip_linux INSTALL_MOD_PATH=~/kakip_linux/modules make modules_install
    ```

3. Verify the build artifact.
    - u-dma-buf.ko

##### 3. mali_km

1. Clone the mali_km repository.
    ```
    # git clone https://github.com/YDS-Kakip-Team/mali_km.git
    # cd mali_km/drivers/gpu/arm/midgard/
    ```

2. Build.
    ```
    # KDIR=~/kakip/kaki/kakip_linux  make
    # KDIR=~/kakip_linux INSTALL_MOD_PATH=~/kakip_linux/modules make modules_install
    ```

3. Verify the build artifact.
    - mali_kbase.ko

##### 4. uvcs_kernel_package

1. Clone the uvcs_kernel_package repository.
    ```
    # git clone https://github.com/YDS-Kakip-Team/uvcs_kernel_package.git
    # cd uvcs_kernel_package/src/makefile
    ```

2. Build.
    ```
    # KDIR=~/kakip/kaki/kakip_linux  make
    # KDIR=~/kakip_linux INSTALL_MOD_PATH=~/kakip_linux/modules make modules_install
    ```

3. Verify the build artifact.
    - uvcs_drv.ko

4. Exit the container after building.
    ```
    # exit
    ```

#### Kernel and Module Update Procedure

##### Deploying Kernel Image and Module Files

1. Mount the SD card to your PC.

    This is the procedure for manually mounting to /mnt.
    If auto-mount is available in your environment, please adjust the mount path accordingly.

    ```
    # sd<X> depends on your environment.
    $ sudo mount /dev/sd<X>2 /mnt
    ```

2. Update the built kernel image.

    ```
    $ sudo cp ~/kakip_linux/arch/arm64/boot/Image /mnt/boot/Image-5.10.145-cip17-yocto-standard
    ```

3. Deploy the built modules.

    Check the module deployment directory.
    ```
    $ ls /mnt/lib/modules/
    ```

    Deploy each module file.
    ```
    $ sudo cp -rv ~/kakip_linux/modules/lib/modules/5.10.145-cip17-yocto-standard/ /mnt/lib/modules/
    ```

4. Unmount the SD card.
    ```
    $ sudo umount /mnt
    ```

##### Boot Verification on Kakip

1. Boot Kakip with the updated SD card.

2. Verify the kernel version.
    ```
    $ uname -r
    5.10.145-cip17-yocto-standard
    ```

3. Verify that the modules are loaded.
    ```
    $ lsmod | grep -E 'mmngr|u_dma_buf|mali_kbase|uvcs_drv'
    ```

4. If everything works properly, the update is complete.

## Notes

- Ensure that the kernel version and module versions match.
- Building modules requires the kernel source tree.
- The module deployment directory may vary depending on the kernel version.
