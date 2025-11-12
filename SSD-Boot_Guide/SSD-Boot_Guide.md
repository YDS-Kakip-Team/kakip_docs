# Kakip NVMe SSD-Boot Guide

Install the Ubuntu system onto an NVMe SSD for the Kakip 8GB (Renesas RZ/V2H).

## Prerequisites

- Kakip 8GB ES4 and above board with OS image v7.4 and above from Kakip official website https://www.kakip.ai/
- [Raspberry Pi SSD Kit](https://www.raspberrypi.com/documentation/accessories/ssd-kit.html#about)

## Installation

### 1. Download the Deployment Script

```bash
wget https://raw.githubusercontent.com/YDS-Kakip-Team/kakip_docs/main/SSD-Boot_Guide/deploy_to_nvme.sh
```

### 2. Download the tarball of kakip os img


```bash
wget <official rootfs download link>
```

#### 2-1. If you want to make your current Ubuntu tarball
```bash
sudo tar --exclude='./home/ubuntu/kakip_rootfs.tgz' --exclude='./dev/*' --exclude='./lost+found' --exclude='./mnt/*' --exclude='./media/*' --exclude='./proc/*' --exclude='./run/*' --exclude='./sys/*' --exclude='./tmp/*' --exclude='./*.deb' --numeric-owner -czpvf ./kakip_rootfs.tgz -C / .
```

## Usage

Follow these steps to deploy the system to your NVMe SSD.

### 1. Run the Deployment Script


```bash
sudo ./deploy_to_nvme.sh
```

### 2. Confirm the Operation
⚠️ **IMPORTANT:** This will **erase all of your SSD data** and **reformat for the Ubuntu system!**

The script will detect your NVMe SSD and ask for confirmation before erasing it.


- Carefully check that the correct drive is listed
- To proceed, type `yes` and press Enter

```
============================ WARNING ============================
This operation will completely erase all data on the drive: /dev/nvme0n1
...
If you are sure you want to continue, type 'yes': yes
```

### 3. Wait for Restoration

The script will partition, format, and restore the system. Timer will show the progress during file extraction.

```
Extracting... 45 seconds have elapsed
```

### 4. Enable SSD Boot

Once the script shows "DEPLOYMENT COMPLETE", run the following command to configure the system to boot from the SSD on the next startup.

```bash
sudo fw_setenv boot_from_ssd yes
```

### 5. Reboot the System

Finally, reboot the board to boot into your new system on the NVMe SSD.

```bash
sudo reboot
```

After rebooting, the system will be running from the NVMe SSD.
