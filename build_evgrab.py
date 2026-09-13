import struct
import keystone

ks = keystone.Ks(keystone.KS_ARCH_ARM64, keystone.KS_MODE_LITTLE_ENDIAN)

asm = r"""
_start:
    ldr x0, [sp]
    cmp x0, #1
    b.gt has_arg
    adr x1, default_path
    b do_open
has_arg:
    ldr x1, [sp, #16]
do_open:
    mov x0, #-100
    mov x2, #0      // try O_RDONLY (0)
    mov x3, #0
    mov x8, #56
    svc #0
    cmp x0, #0
    b.lt err_open
    mov x19, x0

    mov x0, x19
    movz x1, #0x4590
    movk x1, #0x4004, lsl #16
    mov x2, #1
    mov x8, #29
    svc #0
    cmp x0, #0
    b.lt err_ioctl

    // Write GRABBED\n to stdout (fd 1)
    mov x0, #1
    adr x1, msg_grabbed
    mov x2, #8
    mov x8, #64
    svc #0

    sub sp, sp, #64
loop:
    mov x0, x19
    mov x1, sp
    mov x2, #64
    mov x8, #63
    svc #0
    cmp x0, #0
    b.gt loop

exit_clean:
    mov x0, #0
    mov x8, #93
    svc #0

err_open:
    neg x0, x0
    mov x8, #93
    svc #0

err_ioctl:
    neg x0, x0
    add x0, x0, #100
    mov x8, #93
    svc #0

default_path:
    .asciz "/dev/input/event0"
msg_grabbed:
    .ascii "GRABBED\n"
"""

code_ints, count = ks.asm(asm, addr=0x400078)
assert code_ints is not None, "Assembly failed"
code_bytes = bytes(code_ints)

total_len = 0x78 + len(code_bytes)

# Build ELF header (64 bytes)
ehdr = struct.pack(
    '<16sHHIQQQIHHHHHH',
    b'\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00',
    2,       # e_type = ET_EXEC
    183,     # e_machine = EM_AARCH64
    1,       # e_version
    0x400078,# e_entry
    0x40,    # e_phoff
    0,       # e_shoff
    0,       # e_flags
    64,      # e_ehsize
    56,      # e_phentsize
    1,       # e_phnum
    0,       # e_shentsize
    0,       # e_shnum
    0        # e_shstrndx
)

# Build Program Header (56 bytes)
phdr = struct.pack(
    '<IIQQQQQQ',
    1,          # p_type = PT_LOAD
    7,          # p_flags = rwx
    0,          # p_offset
    0x400000,   # p_vaddr
    0x400000,   # p_paddr
    total_len,  # p_filesz
    total_len,  # p_memsz
    0x1000      # p_align
)

elf = ehdr + phdr + code_bytes
with open('/home/golgrax/screen-rescue/evgrab', 'wb') as f:
    f.write(elf)

print(f"Generated evgrab successfully: {len(elf)} bytes")
