import os

class VmsdBase(object):
    KEY = ''

    @classmethod
    def key(cls):
        return cls.KEY

    @classmethod
    def path(cls, path=None):
        if path is None:
            return cls.key()+'.'
        return cls.key()+'.'+path


class VmsdDisk(VmsdBase):
    def __init__(self, num, fileName, node):
        self.num = num
        self.fileName = fileName
        self.node = node

    def get_fileName(self):
        return fileName

    def get_num(self):
        return num

    def get_node(self):
        return node

    @classmethod
    def parse_lines(cls, lines):
        if lines[0].find('disk') != 0:
            return None

        same_disk = set([i.split('.')[0] for i in lines])
        if len(same_disk) != 1:
            return None

        fileName = None
        node = None
        num = None
        disk_key = list(same_disk)[0].strip()

        try:
            num = int(disk_key.replace('disk', ''))
        except:
            pass

        for i in lines:
            if i.find('node') > -1:
                node = i.split('=')[1].strip()
            elif i.find('fileName') > -1:
                fileName = i.split('=')[1].strip()

            if fileName is not None and node is not None:
                break

        if fileName is not None and node is not None and num is not None:
            return VmsdDisk(num, fileName, node)
        return None


class VmsdSnapshot(VmsdBase):
    KEY = 'snapshot'

    def __init__(self, **kargs):
        for k, v in kargs.items():
            setattr(self, k, v)

    def key(self):
        return self.KEY + str(num)

    @classmethod
    def parse_lines(cls, lines):
        kv_dict = {}
        if lines[0].find('snapshot') != 0:
            return None

        same_snapshot = set([i.split('.')[0] for i in lines])
        if len(same_snapshot) != 1:
            return None

        kv_dict['uid'] = None
        kv_dict['num'] = None
        kv_dict['createTimeHigh'] = None
        kv_dict['createTimeLow'] = None
        kv_dict['description'] = None
        kv_dict['disks'] = []
        kv_dict['displayName'] = None
        kv_dict['filename'] = None
        kv_dict['numDisks'] = None
        kv_dict['parent'] = None
        kv_dict['type'] = None
        kv_dict['uid'] = None
        
        num_keys = ['parent', 'uid', 'createTimeLow', 'createTimeHigh', 'numDisks']
        snapshot_key = list(same_snapshot)[0].strip()
        try:
            kv_dict['num'] = int(snapshot_key.replace('snapshot', ''))
        except:
            raise

        kv_dict['disks'] = cls.parse_disks(snapshot_key, lines)
        
        for i in lines:
            i = i.replace(snapshot_key+'.', '')
            key, value = i.split(' = ')
            if key.find('disk') == 0:
                continue
            
            key = key.strip()
            value = value.replace('"', '').strip()

            if key in num_keys:
                kv_dict[key] = int(value.strip())
            elif key in kv_dict:
                kv_dict[key] = value

        return VmsdSnapshot(**kv_dict)

    @classmethod
    def parse_disks(cls, snapshot_id, lines):
        disk_lines = [i for i in lines if i.find('disk') > 0]
        disk_lines = [i.replace(snapshot_id+'.', '') for i in disk_lines]
        disk_keys = set([i.split('.')[0] for i in disk_lines])

        disks = []
        for disk_key in disk_keys:
            ml = [i for i in disk_lines if i.find(disk_key) == 0]
            disk = VmsdDisk.parse_lines(ml)
            if disk is not None:
                disks.append(disk)
        return disks


class VmsdMru(VmsdBase):
    KEY = 'mru'
    KEYS = ['uid']

    def __init__(self, num, uid):
        self.num = num
        self.uid = uid

    def key(self):
        return self.KEY + str(num)

    @classmethod
    def parse_lines(cls, lines):
        if lines[0].find('mru') != 0:
            return None

        same_mru = set([i.split('.')[0] for i in lines])
        if len(same_mru) != 1:
            return None

        uid = None
        num = None
        mru_key = list(same_mru)[0].strip()

        try:
            num = int(mru_key.replace('mru', ''))
        except:
            pass

        for i in lines:
            if i.find('uid') > -1:
                uid = i.split('=')[1].strip().replace('"', '')
                uid = int(uid)
                break

        if uid is not None and num is not None:
            return VmsdMru(num, uid)
        return None

class VmsdSnaphotMeta(VmsdBase):
    KEY = 'snapshot'
    KEYS = [
        'current',
        'lastUID',
        'needConsolidate',
        'numSnapshots',
    ]

    def __init__(self, **kargs):
        for k, v in kargs.items():
            setattr(self, k, v)

    @classmethod
    def parse(cls, lines):
        return cls.parse_lines(lines)

    @classmethod
    def parse_lines(cls, lines):
        kv_dict = {}
        lines = [i for i in lines if i.find('snapshot.') == 0]
        kv_dict['mrus'] = cls.parse_mrus(lines)
        num_keys = ['current', 'lastUID', 'numSnapshots']
        for l in lines:
            if l.find(cls.path(path='mru')) == 0:
                continue

            tokens = '.'.join(l.split('.')[1:]).split()

            key = tokens[0]
            eq_pos = None
            pos = 0
            while pos < len(tokens)-1:
                if tokens[pos] == '=':
                    eq_pos = pos
                    break
                pos += 1

            value = None
            if eq_pos is not None:
                value = '.'.join(tokens[eq_pos+1:]).replace('"', '')
            if key in num_keys:
                value = int(value)
            if key == 'needConsolidate':
                value = value.lower() == str(True).lower() 
            kv_dict[key] = value
        return VmsdSnaphotMeta(**kv_dict)

    @classmethod
    def parse_mrus(cls, lines):
        cp = 'snapshot.mru'
        mru_lines = sorted([i for i in lines if i.find(cp) == 0])

        mru_lines = [i.lstrip('snapshot.') for i in mru_lines]

        mru_keys = set([i.split('.')[0] for i in mru_lines])
        print(mru_keys)
        mrus = []

        for mru_key in mru_keys:
            ml = [i for i in mru_lines if i.find(mru_key) == 0]
            mru = VmsdMru.parse_lines(ml)
            if mru is not None:
                mrus.append(mru)
        return mrus

    def get_current(self):
        getattr(self, 'current', None)

    def get_mrus(self):
        getattr(self, 'mrus', None)

    def get_lastUID(self):
        getattr(self, 'lastUID', None)

    def get_needConsolidate(self):
        getattr(self, 'needConsolidate', None)

    def get_numSnapshots(self):
        getattr(self, 'numSnapshots', None)


class VmsdSnapshots(object):
    EXT = 'vmsd'
    def __init__(self, vm_path, vm_name, ext=EXT):
        self.vmsd_ext = ext
        self.vm_name = vm_name
        self.vm_path = vm_path

        self.meta_info = None
        self.snapshots = None
        self.keyed_snapshots = {}
        
        self.parse_vmsd()

    def parse_vmsd(self):
        filename = '.'.join([self.vm_name, self.vmsd_ext])
        full_path = os.path.join(self.vm_path, filename)

        try:
            os.stat(full_path)
        except:
            raise

        lines = [i.strip() for i in open(full_path).readlines() if len(i.strip()) > 0]

        self.snapshots = self.parse_snapshots(lines)
        for snapshot in self.snapshots:
            name = snapshot.displayName
            num = snapshot.num
            self.keyed_snapshots[num] = snapshot
            self.keyed_snapshots[name] = snapshot

        self.meta_info = VmsdSnaphotMeta.parse_lines(lines)

    def parse_snapshots(self, lines):
        is_snapshot = lambda l: len(l) > len('snapshot.') and l.replace('snapshot', '').split('.')[0].isdigit()
        snapshot_lines = sorted([i for i in lines if is_snapshot(i)])
        snapshot_keys = set([i.split('.')[0] for i in snapshot_lines])
        snapshots = []

        for snapshot_key in snapshot_keys:
            ml = [i for i in snapshot_lines if i.find(snapshot_key) == 0]
            snapshot = VmsdSnapshot.parse_lines(ml)
            if snapshot is not None:
                snapshots.append(snapshot)
        return snapshots

    def get_snapshot_memory_path(self, name=None, num=None):
        filename = None
        ss = None
        if name is not None and name in self.keyed_snapshots:
            ss = self.keyed_snapshots[name]
        elif num is not None and num in self.keyed_snapshots:
            ss = self.keyed_snapshots[name]

        if ss is None:
            return None
        filename = ss.fileName
        return os.path.join(self.vm_path, filename)

    def get_snapshot_disk_path(self, name=None, num=None, disk_num=0):
        filename = None
        ss = None
        if name is not None and name in self.keyed_snapshots:
            ss = self.keyed_snapshots[name]
        elif num is not None and num in self.keyed_snapshots:
            ss = self.keyed_snapshots[name]

        if ss is None:
            return None

        disk = None
        for _disk in ss.disks:
            if _disk.num == disk_num:
                disk = _disk
                break
        if disk is not None:
            filename = fileName
        return os.path.join(self.vm_path, filename)
