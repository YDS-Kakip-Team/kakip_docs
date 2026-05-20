# Kakip CAN FD Example (CH0 <-> CH3) for CM33 / CR8

A CAN FD loopback example using CANFD channel 0 and channel 3 on the Kakip board. The firmware sends user-typed messages via Classic CAN (8 bytes) and CAN FD (64 bytes) between two channels on the same board, demonstrating both frame types.

## Prerequisites

- Kakip board with OS image from Kakip official website <https://www.kakip.ai/>
- USB-UART adapter (e.g., Pmod USBUART, FTDI cable)
- CAN FD loopback cable (connects CAN CH0 and CH3 on board)
- Serial terminal software (TeraTerm, minicom, etc.)
- e2 studio with RZ/V2H FSP v3.0.0
- GCC ARM Embedded toolchain (13.3.1.arm-13-24)

> **Note:** This project is built with FSP v3.0.0. Using a different FSP version may cause build errors.
> Prebuilt firmware binaries are available in the [firmware/](firmware/) directory for quick testing without building.

## Hardware Connection

### UART Console

Connect the USB-UART adapter to the **40-pin GPIO header (CN6)** for serial output:

| CN6 Pin | Signal                  | Connect to           |
| ------- | ----------------------- | -------------------- |
| 6       | GND                     | Adapter GND from PC  |
| 8       | GPIO14 (P7_2) RSCI5_TXD | Adapter RXD from PC  |
| 10      | GPIO15 (P7_3) RSCI5_RXD | Adapter TXD from PC  |

### CAN FD Loopback

Connect the CAN FD loopback cable between CH0 and CH3 on the Kakip board. The CAN transceivers (IC12) are enabled by firmware via STB pins (P10_2, P10_3).

![Hardware Setup](image/hardware_setup.jpg)

## Build

### 1. Clone the Repository

```bash
$ git clone https://github.com/YDS-Kakip-Team/kakip_cm33_cr8_example.git
```

### 2. Apply Kernel Patches

Apply the following patches to the Kakip Linux kernel source.
Without these patches, the CAN and UART will stop working after Linux boots.

```bash
$ cd <kakip_linux>
$ git apply <repo_path>/kakip_canfd_example/kakip_linux/arch/arm64/boot/dts/renesas/kakip-es1.dts.diff
$ git apply <repo_path>/kakip_canfd_example/kakip_linux/drivers/clk/renesas/r9a09g057-cpg.c.diff
```

| Patch | Purpose |
|-------|---------|
| `kakip-es1.dts.diff` | Disable `&canfd` and `&sci5` to prevent Linux drivers from probing |
| `r9a09g057-cpg.c.diff` | Mark CANFD and RSCI5 clocks as critical to prevent clock gating |

> **Important:** Rebuild the kernel and deploy the updated Image and DTB to the SD card.
> For kernel build and deploy instructions, refer to the [Kernel Update Guide](../../Kernel-Update_Guide/Kernel-Update_Guide.md).

### 3. Build Projects

For e2 studio import, preceding project build, generate project content, and build instructions, refer to the [Kakip UART Example Guide (Kakip_UART_Example_Guide.md)](../uart_example/Kakip_UART_Example_Guide.md#3-open-e2-studio-and-import-projects).

### Build Output

| Core | Binary | Location |
|------|--------|----------|
| CM33 | `can_fd_kakip_cm33_ep.bin` | `Release/` |
| CR8_0 | `can_fd_kakip_cr8_0_ep_itcm.bin` + `_sram.bin` | `Release/` |
| CR8_1 | `can_fd_kakip_cr8_1_ep_itcm.bin` + `_sram.bin` | `Release/` |

## Deploy

Insert the Kakip SD card into the host PC and mount the boot partition:

```bash
# Check the device name (e.g., /dev/sdb)
$ lsblk

# Mount the boot partition (partition 1)
$ sudo mount /dev/sd<X>1 /mnt
```

Copy all firmware binaries to the boot partition:

```bash
# CM33
$ sudo cp can_fd_kakip_cm33_ep.bin /mnt/

# CR8_0
$ sudo cp can_fd_kakip_cr8_0_ep_itcm.bin /mnt/
$ sudo cp can_fd_kakip_cr8_0_ep_sram.bin /mnt/

# CR8_1
$ sudo cp can_fd_kakip_cr8_1_ep_itcm.bin /mnt/
$ sudo cp can_fd_kakip_cr8_1_ep_sram.bin /mnt/

$ sudo umount /mnt
```

## Run

Stop at the U-Boot prompt (`=>`) by pressing any key during boot. Load **one** firmware at a time, then boot Linux.

> **Note:** These projects are independent and share the same UART port (SCI5). Only run one at a time.

### CM33

```
=> setenv cm33start 'dcache off; mw.l 0x10420D2C 0x02000000; mw.l 0x1043080c 0x08003000; mw.l 0x10430810 0x18003000; mw.l 0x10420604 0x00040004; mw.l 0x10420C1C 0x00003100; mw.l 0x10420C0C 0x00000001; mw.l 0x10420904 0x00380008; mw.l 0x10420904 0x00380038; fatload mmc 0:1 0x08001e00 can_fd_kakip_cm33_ep.bin; mw.l 0x10420C0C 0x00000000; dcache on'
=> saveenv
=> run cm33start
=> boot
```

### CR8_0

```
=> setenv cr8start 'dcache off; mw.l 0x10420D24 0x04000000; mw.l 0x10420600 0xE000E000; mw.l 0x10420604 0x00030003; mw.l 0x10420908 0x1FFF0000; mw.l 0x10420C44 0x003F0000; mw.l 0x10420C14 0x00000000; mw.l 0x10420908 0x10001000; mw.l 0x10420C48 0x00000020; mw.l 0x10420908 0x1FFF1FFF; mw.l 0x10420C48 0x00000000; fatload mmc 0:1 0x12040000 can_fd_kakip_cr8_0_ep_itcm.bin; fatload mmc 0:1 0x08180000 can_fd_kakip_cr8_0_ep_sram.bin; mw.l 0x10420C14 0x00000003; dcache on;'
=> saveenv
=> run cr8start
=> boot
```

### CR8_1

```
=> setenv cr81start 'dcache off; mw.l 0x10420D24 0x04000000; mw.l 0x10420600 0xE000E000; mw.l 0x10420604 0x00030003; mw.l 0x10420908 0x1FFF0000; mw.l 0x10420C44 0x003F0000; mw.l 0x10420C14 0x00000000; mw.l 0x10420908 0x10001000; mw.l 0x10420C48 0x00000020; mw.l 0x10420908 0x1FFF1FFF; mw.l 0x10420C48 0x00000000; fatload mmc 0:1 0x12080000 can_fd_kakip_cr8_1_ep_itcm.bin; fatload mmc 0:1 0x081C0000 can_fd_kakip_cr8_1_ep_sram.bin; mw.l 0x10420C14 0x00000003; dcache on;'
=> saveenv
=> run cr81start
=> boot
```

## Expected Results

Type a message and press Enter. The firmware sends the message via Classic CAN (first 8 bytes only) and CAN FD (full 64 bytes) between CH0 and CH3, then prints the results.

> **Note:** Classic CAN only transmits the first 8 bytes of user input. CAN FD transmits up to 64 bytes.

![CAN FD Terminal Output](image/can_fd_terminal_output.png)

## Troubleshooting

### CAN transmission timeout

**Cause:** CAN transceiver not enabled, or Linux clock gating disabled the CANFD module.
**Solution:** Ensure kernel patches are applied. The firmware drives STB pins LOW to enable transceivers.

### UART stops working after Linux boots

**Cause:** Linux CPG driver gates the SCI5 clock.
**Solution:** Apply the kernel patches (see Build Step 2).

### e2 studio: "Invalid device family context"

**Cause:** Preceding project was renamed.
**Solution:** Keep original name `preceding_rzv2h_evk_cm33_ep`.

### e2 studio: "Smart Bundle file is missing"

**Cause:** Preceding project not built yet.
**Solution:** Build `preceding_rzv2h_evk_cm33_ep` first (see [Kakip UART Example Guide (Kakip_UART_Example_Guide.md)](../uart_example/Kakip_UART_Example_Guide.md#4-build-preceding-project-required-for-cr8)).

### CR8: "cannot open linker script file memory_regions.ld"

**Cause:** Generate Project Content not executed.
**Solution:** Open `configuration.xml` -> **Generate Project Content** -> Build.
