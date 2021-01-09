#!/usr/bin/env python3
from pwn import *
import os.path
# context.log_level = 'debug'

images_base = './images'

# Speed things up by using a snapshot to load machine state saved just after
# logging into the system
use_snapshot = True

if use_snapshot:
	cmd = f'''qemu-system-arm \
		-M versatilepb \
		-kernel {images_base}/zImage \
		-dtb {images_base}/versatile-pb.dtb \
		-drive file={images_base}/rootfs.qcow2,if=scsi \
		-append "root=/dev/sda console=ttyAMA0,115200" \
		-net nic,model=rtl8139 -net user,hostfwd=tcp:127.0.0.1:2222-:2222 \
		-name Versatile_ARM_EXT2 \
		-display none -nographic \
		-loadvm loggedin
	'''
else:
	cmd = f'''qemu-system-arm \
		-M versatilepb \
		-kernel {images_base}/zImage \
		-dtb {images_base}/versatile-pb.dtb \
		-drive file={images_base}/rootfs.ext2,if=scsi,format=raw -snapshot \
		-append "root=/dev/sda console=ttyAMA0,115200" \
		-net nic,model=rtl8139 -net user,hostfwd=tcp:127.0.0.1:2222-:2222 \
		-name Versatile_ARM_EXT2 \
		-display none -nographic \
	'''

p = process(cmd, True)
if use_snapshot:
	p.sendline('')
else:
	p.recvuntil('login:')
	p.sendline('root')
p.recvuntil('#')

# Note: This expects that netcat is installed on the system. Alternatively you
# could pipe files through your shell, read/write them on disk before and after
# launching, etc
def send_file(path, outfile=None):
	outfile = outfile or os.path.basename(path)

	# Open a socket on guest (forwarded through QEMU above)
	p.sendline('nc -l -p 2222 > ' + outfile)
	sleep(0.125)

	# Pipe the file over
	s = remote('127.0.0.1', 2222)
	s.send(open(path, 'rb').read())
	s.close()

	# Wait for shell to come back and mark the file executable
	p.recvuntil('#')
	p.sendline('chmod +x ' + outfile)
	p.recvuntil('#')

def recv_file(path, outfile=None):
	outfile = outfile or os.path.basename(path)

	# Open a socket on guest (forwarded through QEMU above)
	p.sendline('cat ' + path + ' | nc -l -p 2222 -c')
	sleep(0.125)

	# Pipe the file over
	s = remote('127.0.0.1', 2222)
	open(outfile, 'wb').write(s.recvall())
	s.close()

	# Wait for shell to come back
	p.recvuntil('#')

# Enable core dumps
p.sendline('ulimit -c unlimited')
p.recvuntil('#')
p.sendline('echo "core" > /proc/sys/kernel/core_pattern')
p.recvuntil('#')

crashaddr = ELF('target').symbols['patchcrash']

# Run target binary, grab the core dump
send_file('crasher.so')
send_file('target')
p.sendline('CRASHADDR=%x LD_PRELOAD=$PWD/crasher.so ./target' % (crashaddr))
output = p.recvuntil('#', timeout=1).decode('utf-8')
if 'core dumped' in output:
	recv_file('core')
print(output)

p.kill()
