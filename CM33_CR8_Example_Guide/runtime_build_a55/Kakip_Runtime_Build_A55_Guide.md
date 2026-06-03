# Kakip Native Build on Board (Makefile System)

Build CM33 / CR8 firmware **directly on the Kakip board** with `make`. No e2 studio needed on the board.

## Prerequisites

- Kakip board with OS image from <https://www.kakip.ai/>
- Internet access on the board (toolchain download, ~140 MB, one-time)
- A project that has already been opened in e2 studio on the host PC and built once via **Generate Project Content** (so `rzv/`, `rzv_gen/`, `rzv_cfg/`, `script/`, `Release/memory_regions.ld` exist)

> Each `make` step below applies to the project under its own `e2studio/` directory. Replace `<project>` paths with your target.

## Step 1 — Transfer Repo to the Board

> Run on **host PC** (SD card removed from board and inserted in host).

```bash
$ lsblk                                              # find your SD card, e.g. /dev/sdb
$ sudo mount /dev/sd<X>2 /mnt                        # rootfs partition (ext4, partition 2)
$ sudo cp -r kakip_cm33_cr8_example /mnt/home/ubuntu/
$ sudo umount /mnt
```

Put the SD card back in the board and boot.

## Step 2 — Install Toolchain (one-time)

> Run on **Kakip board** (over SSH or serial).

```bash
$ cd ~/kakip_cm33_cr8_example
$ ./setup.sh
$ export PATH=/opt/arm-gnu-toolchain/bin:$PATH
```

![Setup Script](image/setup_sh.png)

Optional: append the `export` line to `~/.bashrc` so new shells have it.

## Step 3 — Build a Project

> Run on **Kakip board**.

```bash
$ cd ~/kakip_cm33_cr8_example/kakip_uart_example/sci_b_uart_kakip_cr8_0_ep/e2studio
$ make
```

![Build Output](image/build_output.png)

Output files appear in the same `e2studio/` directory:

| Core | Output |
|------|--------|
| CM33 | `<project>.bin` |
| CR8_0 / CR8_1 | `<project>_itcm.bin`, `<project>_sram.bin`, `<project>_header.bin` |

To rebuild from scratch: `make clean && make`.

## Step 4 — Install to SD Card

> Run on **Kakip board**, still inside the project's `e2studio/` directory.

```bash
$ sudo mount /dev/mmcblk0p1 /mnt
$ sudo PATH=$PATH make install
$ sudo umount /mnt
```

`make install` copies the project's `.bin` files to `/mnt/` (the SD card boot partition).

> `sudo PATH=$PATH` is required so `sudo` keeps the toolchain in PATH for the `make` invocation.

![Make Install](image/make_install.png)

## Step 5 — Run

Reboot, stop at U-Boot, then follow the **Run** section of the matching example guide. The U-Boot commands are identical across IDE-built and natively built firmware.

| Example | Run instructions |
|---------|------------------|
| UART | [Kakip UART Example Guide](../uart_example/Kakip_UART_Example_Guide.md#run) |
| FreeRTOS | [Kakip FreeRTOS Example Guide](../freertos/Kakip_FreeRTOS_Example_Guide.md#run) |
| CAN FD | [Kakip CAN FD Example Guide](../can_fd/Kakip_CAN_FD_Example_Guide.md#run) |
| GPIO IO | [Kakip GPIO IO Example Guide](../gpio_io/Kakip_GPIO_IO_Example_Guide.md#run) |

## Project List

Every project below has a Makefile that uses the shared `common.mk`. The `cd && make` flow in Step 3 applies to all of them.

| Project | Path under repo root |
|---------|----------------------|
| UART CR8_0 | `kakip_uart_example/sci_b_uart_kakip_cr8_0_ep/e2studio` |
| UART CR8_1 | `kakip_uart_example/sci_b_uart_kakip_cr8_1_ep/e2studio` |
| UART CM33 | `kakip_uart_example/sci_b_uart_kakip_cm33_ep/e2studio` |
| CAN FD CR8_0 | `kakip_canfd_example/can_fd_kakip_cr8_0_ep/e2studio` |
| CAN FD CR8_1 | `kakip_canfd_example/can_fd_kakip_cr8_1_ep/e2studio` |
| CAN FD CM33 | `kakip_canfd_example/can_fd_kakip_cm33_ep/e2studio` |
| GPIO IO CR8_0 | `kakip_gpio_io_example/gpio_io_kakip_cr8_0_ep/e2studio` |
| GPIO IO CR8_1 | `kakip_gpio_io_example/gpio_io_kakip_cr8_1_ep/e2studio` |
| GPIO IO CM33 | `kakip_gpio_io_example/gpio_io_kakip_cm33_ep/e2studio` |
| FreeRTOS CR8_0 | `kakip_rtos_example/freertos_kakip_cr8_0_ep/e2studio` |
| FreeRTOS CR8_1 | `kakip_rtos_example/freertos_kakip_cr8_1_ep/e2studio` |
| FreeRTOS CM33 | `kakip_rtos_example/freertos_kakip_cm33_ep/e2studio` |
| remoteproc CM33 | `kakip_remoteproc/rzv2h_cm33_rpmsg_linux-rtos_demo` |

> **Note:** `kakip_remoteproc/rzv2h_cm33_rpmsg_linux-rtos_demo` has the Makefile in the project root (no `e2studio/` subdirectory). For Step 3, `cd` into that directory directly. For Step 4 — deployment and runtime usage are covered by the [Kakip CM33 Remoteproc Guide](../remoteproc/Kakip_CM33_Remoteproc_Guide.md), not by Step 5 of this guide.

## Troubleshooting

### `arm-none-eabi-gcc not found`

```
common.mk:28: *** arm-none-eabi-gcc not found. Run: export PATH=/opt/arm-gnu-toolchain/bin:$PATH
```

→ `export PATH=/opt/arm-gnu-toolchain/bin:$PATH` (current shell only; add to `~/.bashrc` for permanent).

### `make install` fails: toolchain not found under sudo

→ Use `sudo PATH=$PATH make install`. Plain `sudo` strips PATH.

### `cannot open linker script file memory_regions.ld`

→ The project was never run through **Generate Project Content** in e2 studio. Open it on the host PC, generate, then re-transfer (Step 1).

---

## Adding a New Project

The Makefile in each project is intentionally tiny — two variables, then it includes the shared rules:

```makefile
PROJECT_NAME = sci_b_uart_kakip_cr8_0_ep
CORE         = CR8_0          # CR8_0 / CR8_1 / CM33

include ../../../common.mk
```

To add a new project, create a `Makefile` like the above under its `e2studio/` directory. The `CORE` variable drives all per-core differences (CPU flags, linker script, output mode). No changes to `common.mk` are required as long as the project keeps the standard e2 studio FSP layout (`src/`, `rzv/`, `rzv_gen/`, `rzv_cfg/`, `script/`, `Release/memory_regions.ld`).
