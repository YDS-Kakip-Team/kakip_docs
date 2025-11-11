#!/bin/bash

set -e

if [[ $EUID -ne 0 ]]; then
   echo "Error: This script must be run as root. Please use 'sudo ./deploy_to_nvme.sh'"
   exit 1
fi

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

ROOTFS_TAR=$(ls "$SCRIPT_DIR"/kakip*rootfs.tgz | head -n 1)

# Check if a file was found at all.
if [[ ! -f "$ROOTFS_TAR" ]]; then
    echo "Error: Could not find a rootfs archive matching 'kakip*rootfs.tgz'." >&2
    exit 1
fi

echo "Using rootfs archive: $(basename "$ROOTFS_TAR")"
echo ""


# Find the first NVMe drive
echo "Searching for NVMe drive..."
NVME_DEVICE=$(ls /dev/nvme*n1 | head -n 1)

if [[ -z "$NVME_DEVICE" ]]; then
    echo "Error: No NVMe drive found (e.g., /dev/nvme0n1)." >&2
    exit 1
fi
echo "Drive found: $NVME_DEVICE"
echo ""

# User confirmation prompt
echo "============================ WARNING ============================"
echo "This operation will completely erase all data on the drive: $NVME_DEVICE"
echo "The drive will be re-partitioned, formatted, and a new Ubuntu system will be installed."
echo "This process is irreversible!"
echo "======================================================================="
read -p "If you are sure you want to continue, type 'yes': " confirmation

if [[ "$confirmation" != "yes" ]]; then
    echo "Operation canceled."
    exit 0
fi

echo "Starting deployment..."

# Get drive size in bytes
echo "Detecting drive capacity..."
DISK_SIZE_BYTES=$(lsblk -b -d -o SIZE "$NVME_DEVICE" | tail -n 1)
# 4 TiB in bytes (1024^4)
FOUR_TB_IN_BYTES=$((4 * 1024 * 1024 * 1024 * 1024))

# For safety, try to unmount the partition first in case it's auto-mounted
umount "${NVME_DEVICE}p1" 2>/dev/null || true

# Step 1: Re-partition the drive
echo "Partitioning $NVME_DEVICE..."
if [[ $DISK_SIZE_BYTES -gt $FOUR_TB_IN_BYTES ]]; then
    echo "Capacity is larger than 4TB, using GPT partition table."
    parted -s "$NVME_DEVICE" mklabel gpt
else
    echo "Capacity is less than or equal to 4TB, using MBR (msdos) partition table."
    parted -s "$NVME_DEVICE" mklabel msdos
fi

parted -s -a optimal "$NVME_DEVICE" mkpart primary ext4 0% 100%
sleep 2 # Wait for the kernel to recognize the new partition

PARTITION="${NVME_DEVICE}p1"
echo "Partition ${PARTITION} has been created."

# Step 2: Format the new partition
echo "Formatting ${PARTITION} as ext4..."
mkfs.ext4 -F "$PARTITION"

# Step 3: Mount the partition and restore the rootfs
echo "Restoring root filesystem..."

MOUNT_POINT="/mnt/new_rootfs"
mkdir -p "$MOUNT_POINT"
mount "$PARTITION" "$MOUNT_POINT"

echo "Extracting '$(basename "$ROOTFS_TAR")' to ${PARTITION}, this may take a few minutes..."

# Run tar in the background
tar -xzpf "$ROOTFS_TAR" -C "$MOUNT_POINT" &
TAR_PID=$!

# Start the timer
SECONDS_COUNTER=0
while ps -p $TAR_PID > /dev/null; do
    printf "\rExtracting... %s seconds have elapsed" "$SECONDS_COUNTER"
    sleep 1
    SECONDS_COUNTER=$((SECONDS_COUNTER + 1))
done

echo ""

if ! wait $TAR_PID; then
    echo "Error: An error occurred during extraction!" >&2
    umount "$MOUNT_POINT" 2>/dev/null || true
    rmdir "$MOUNT_POINT" 2>/dev/null || true
    exit 1
fi

echo "Extraction complete."
sync

# Step 4: Clean up
echo "Unmounting partition..."
umount "$MOUNT_POINT"
rmdir "$MOUNT_POINT"

echo ""
echo "======================== DEPLOYMENT COMPLETE ========================"
echo "The Ubuntu system has been successfully installed on $NVME_DEVICE."
echo "You can set nvme_boot (sudo fw_setenv boot_from_ssd yes) and reboot (sudo reboot) to boot from the NVMe drive."
echo "======================================================================="

exit 0

