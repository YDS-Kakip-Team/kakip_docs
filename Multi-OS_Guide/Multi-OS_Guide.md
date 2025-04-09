# Multi-OS 対応手順書

## CM33/CR8の起動

1. u-bootで以下のコマンドを実行する
    
    - CM33の起動

        ```
        => setenv cm33start 'dcache off; mw.l 0x10420D2C 0x02000000; mw.l 0x1043080c 0x08003000; mw.l 0x10430810 0x18003000; mw.l 0x10420604 0x00040004; mw.l 0x10420C1C 0x00003100; mw.l 0x10420C0C 0x00000001; mw.l 0x10420904 0x00380008; mw.l 0x10420904 0x00380038; ext4load mmc 0:2 0x08001e00 boot/rzv2h_cm33_rpmsg_demo.bin; mw.l 0x10420C0C 0x00000000; dcache on'
        => saveenv
        => run cm33start
        ```

    - CR8の起動

        ```
        => setenv cr8start 'dcache off; mw.l 0x10420D24 0x04000000; mw.l 0x10420600 0xE000E000; mw.l 0x10420604 0x00030003; mw.l 0x10420908 0x1FFF0000; mw.l 0x10420C44 0x003F0000; mw.l 0x10420C14 0x00000000; mw.l 0x10420908 0x10001000; mw.l 0x10420C48 0x00000020; mw.l 0x10420908 0x1FFF1FFF; mw.l 0x10420C48 0x00000000; ext4load mmc 0:2 0x12040000 boot/rzv2h_cr8_rpmsg_demo_itcm.bin; ext4load mmc 0:2 0x08180000 boot/rzv2h_cr8_rpmsg_demo_sram.bin; ext4load mmc 0:2 0x40800000 boot/rzv2h_cr8_rpmsg_demo_sdram.bin; mw.l 0x10420C14 0x00000003; dcache on;'
        => saveenv
        => run cr8start
        ```

    ※ setenv時に以下の表示がされ、設定できない場合は本資料最下部の「既知の問題」を参照
    ```
    Unknown command 'setenv' - try 'help'
    ```

2. カーネルを起動する

    ```
    => run bootcmd
    ```

## 動作確認
ログイン後、rpmsg_sample_clientを実行。以下のような表示であることを確認する。
詳しい動作確認手順は[公式ドキュメント](https://www.renesas.com/en/document/rln/release-note-rzv-multi-os-package-v210?language=en)を参照のこと。

```
$ sudo rpmsg_sample_client
[1116] proc_id:0 rsc_id:0 mbx_id:1
metal: warning:   metal_linux_irq_handling: Failed to set scheduler: -1.
metal: info:      metal_uio_dev_open: No IRQ for device 10480000.mbox-uio.
[1116] Successfully probed IPI device
metal: info:      metal_uio_dev_open: No IRQ for device 42f00000.rsctbl.
[1116] Successfully open uio device: 42f00000.rsctbl.
[1116] Successfully added memory device 42f00000.rsctbl.
metal: info:      metal_uio_dev_open: No IRQ for device 43000000.vring-ctl0.
[1116] Successfully open uio device: 43000000.vring-ctl0.
[1116] Successfully added memory device 43000000.vring-ctl0.
metal: info:      metal_uio_dev_open: No IRQ for device 43200000.vring-shm0.
[1116] Successfully open uio device: 43200000.vring-shm0.
[1116] Successfully added memory device 43200000.vring-shm0.
metal: info:      metal_uio_dev_open: No IRQ for device 43100000.vring-ctl1.
[1116] Successfully open uio device: 43100000.vring-ctl1.
[1116] Successfully added memory device 43100000.vring-ctl1.
metal: info:      metal_uio_dev_open: No IRQ for device 43500000.vring-shm1.
[1116] Successfully open uio device: 43500000.vring-shm1.
[1116] Successfully added memory device 43500000.vring-shm1.
metal: info:      metal_uio_dev_open: No IRQ for device 42f01000.mhu-shm.
[1116] Successfully open uio device: 42f01000.mhu-shm.
[1116] Successfully added memory device 42f01000.mhu-shm.
[1116] Initialize remoteproc successfully.
[1116] proc_id:1 rsc_id:1 mbx_id:1
[1116] Initialize remoteproc successfully.
[1116] proc_id:0 rsc_id:0 mbx_id:2
[1116] Initialize remoteproc successfully.
[1116] proc_id:1 rsc_id:1 mbx_id:2
[1116] Initialize remoteproc successfully.
[1116] proc_id:0 rsc_id:0 mbx_id:3
[1116] Initialize remoteproc successfully.
[1116] proc_id:1 rsc_id:1 mbx_id:3
[1116] Initialize remoteproc successfully.
 
******************************************
*   rpmsg communication sample program   *
******************************************
 
1. communicate with CM33      ch0
2. communicate with CM33      ch1
3. communicate with CR8 core0 ch0
4. communicate with CR8 core0 ch1
5. communicate with CR8 core1 ch0
6. communicate with CR8 core1 ch1
7. communicate with CM33 ch0 and CR8 core0 ch1
8. communicate with CM33 ch0 and CR8 core1 ch1
9. communicate with CR8 core0 ch0 and CR8 core1 ch1
 
 
e. exit
 
please input
>
```

## 既知の問題

### u-bootにてsetenvが行えない
u-bootでのsetenv時に、コマンドが見つからないと表示され、設定が行えない。

```
=> setenv cm33start 'dcache off; mw.l 0x10420D2C 0x02000000; mw.l 0x1043080c 0x08003000; mw.l 0x10430810 0x18003000; mw.l 0x10420604 0x00040004; mw.l 0x10420C1C 0x00003100; mw.l 0x10420C0C 0x00000001; mw.l 0x10420904 0x00380008; mw.l 0x10420904 0x00380038; ext4load mmc 0:2 0x08001e00 boot/rzv2h_cm33_rpmsg_demo.bin; mw.l 0x10420C0C 0x00000000; dcache on'
Unknown command 'setenv' - try 'help'
```

#### 対処法
Kakipを再起動することで解消される。