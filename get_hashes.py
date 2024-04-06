import hashlib
import os

if __name__ == '__main__':
    base = 'G:\\.shortcut-targets-by-id\\1AW0W0amolgf4yzIMhgs_fcpbkvR37Tqz\\Say My Name runs'
    for file in os.listdir(base):
        if os.path.isdir(os.path.join(base, file)):
            continue
        lfile = hashlib.md5(open(os.path.join(base, file), 'rb').read()).hexdigest()
        print(file, lfile)