Setup
-----

### buildroot
```bash
wget https://buildroot.org/downloads/buildroot-2020.02.9.tar.gz
tar xvf buildroot-2020.02.9.tar.gz
cd buildroot-2020.02.9
make qemu_arm_versatile_defconfig
make menuconfig
# Enable netcat in package settings
make
```

### run
```bash
qemu-system-arm \
	-M versatilepb \
	-kernel output/images/zImage \
	-dtb output/images/versatile-pb.dtb \
	-drive file=output/images/rootfs.ext2,if=scsi,format=raw -snapshot \
	-append "root=/dev/sda console=ttyAMA0,115200" \
	-net nic,model=rtl8139 -net user \
	-name Versatile_ARM_EXT2 \
	-display none -nographic
# C-a x to exit.
```

I've moved rootfs.ext2 to qcow2 format:

```bash
qemu-img convert -f raw -O qcow2 buildroot-2020.02.9/output/images/rootfs.ext2 rootfs.qcow2
```

Then boot and login as root. Switch over to QEMU monitor (C-a c) and create
a snapshot with `savevm loggedin`. Then quit (C-a x).

Update launch.py with correct paths.

### Python

Install pwntools before running launch.py

Crash Methods
-------------
- Method 1: Simple little LD_PRELOAD lib that crashes at address CRASHADDR

Run
---

```bash
make && launch.py
```

Build target and crasher lib. Launches QEMU, moves target and crasher lib over,
runs target, then retrieves core dump to be loaded in gdb.

Analysis
--------
Load core dump with gdb:

```
./buildroot-2020.02.9/output/host/bin/arm-buildroot-linux-uclibcgnueabi-gdb
(gdb) core core
```

---

FIXME: If necessary gen Docker image with kernel+rootfs+toolchain ready to go
