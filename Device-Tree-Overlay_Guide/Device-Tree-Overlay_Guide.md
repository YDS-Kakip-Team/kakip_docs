# Overlay files:
**40-PIN header:**<br>
kakip-es1-spi0.dtbo: GPIO7, GPIO8, GPIO9, GPIO10, GPIO11 => SPI0 mode<br>
kakip-es1-pwm0.dtbo: GPIO12 => PWM0 mode<br>
kakip-es1-pwm1.dtbo: GPIO 13 => PWM1 mode<br>
kakip-es1-sci5-to-gpio.dtbo: SCI5 mode => GPIO14, GPIO15<br>
kakip-es1-i2c10.dtbo: I2C10 mode => GPIO2, GPIO3 <br>

**Accessories:**<br>
kakip-es1-imx219.dtbo => IMX219 camera <br>
kakip-es1-imx462.dtbo => e-CON IMX462 camera（e-CAM22_CURZH）<br>
kakip-es1-tc358743.dtbo => X1301 HDMI-IN HAT


# How to load dtbo files using libubootenv

Step 1. boot into Ubuntu system and login.

Step 2. Issue command to checking the bootargs status

    $ sudo fw_printenv
    ... ignore ...
    boot_fdt_overlay=no
    ... ignore ...
    fdt_overlay_files=kakip-es1-spi0
    ... ignore ...
    ... ignore ...

    boot_fdt_overlay is the overlay switch, default is disabled.
    fdt_overlay_files is the overlay files which you want to loaded, it works when boot_fdt_overlay was be enabled.

Step 3. enable overlay function

    $ sudo fw_setenv boot_fdt_overlay yes

    It will auto load dtbo according your 'fdt_overlay_files' definition

Step 4. change the overlay files

    Enabling SPI function
    $ sudo fw_setenv fdt_overlay_files kakip-es1-spi0

    Enabling PWM0 function
    $ sudo fw_setenv fdt_overlay_files kakip-es1-pwm0

    Enabling PWM1 function
    $ sudo fw_setenv fdt_overlay_files kakip-es1-pwm1

    Disabling SCI5 function and change to GPIO mode
    $ sudo fw_setenv fdt_overlay_files kakip-es1-sci5-to-gpio

    It also support multiple dtbo files at the same time.
    Example, Enabling SPI0, PWM0 and PWM1:
    $ sudo fw_setenv fdt_overlay_files 'kakip-es1-spi0 kakip-es1-pwm0 kakip-es1-pwm1'

Step 5. Issue the reboot command, then overlay function will be auto stored, you can checking the bootargs using fw_printenv.
    $ sudo reboot

Note that due to the nature of the PWM driver, there is a specific order in which PWM nodes must be enabled. If you only have the overlay for either pwm0 or pwm1 node, you will only see pwm0 interface in userspace.

In addition, Disabling overlay function, back to original 40-PIN status

    $ sudo fw_setenv boot_fdt_overlay no
    $ sudo reboot
