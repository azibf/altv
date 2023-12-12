from proxmoxer import ProxmoxAPI

proxmox = ProxmoxAPI('77.106.68.24', user='root@pam', password='1H6b0Z8c8J', verify_ssl=False, service='PVE')

class Pool:
    def __init__(self, name, node, golden_image):
        self.name = name
        self.node = node
        self.gi = golden_image
        self.pool = []
        
        
    def create(self, c):
        vmids = []
        max_vmid = max([vm['vmid'] for vm in self.node.qemu.get()])
        start = max_vmid
        for i in range(c):
            max_vmid += 1
            self.gi.clone.post(newid=max_vmid)
            print(f"CREATED VM {max_vmid}")
            vmids.append(max_vmid)
        #while len(vmids) != 0:
        #    for elem in self.node.tasks.get():
        #        if (elem['id'].isdigit()):
        #            if int(elem['id']) in vmids and elem['type'] == 'qmclone' and elem['status'] == 'OK':
        #                vmids.remove(int(elem['id']))
        while not(all(map(lambda x: x in [vm['vmid'] for vm in self.node.qemu.get()], vmids))):
            continue
        for i in range(start + 1, max_vmid + 1):
            self.pool.append(self.node.qemu(i))
            print(self.node.qemu(i))

            
    def check(self):
        for vm in self.pool:
            print(vm['status'])
            
    def delete(self):
        for vm in self.pool:
            vm.delete()
    
    def stop(self):
        try:
            for vm in self.pool:
                vm.status.stop.post()
                print(f"VM {vm['vmid']} STOPPED")
        except:
            print("ERROR DURING STOP POOL")
    
    def start(self):
        try:
            for vm in self.pool:
                vm.status.start.post()
                print(f"VM {vm['vmid']} STARTED")
        except:
            print("ERROR DURING STARTING POOL")
    
    def shutdown(self):
        try:
            for vm in self.pool:
                vm.status.shutdown.post()
                print(f"VM {vm['vmid']} SHUTTED DOWN")
        except:
            print("ERROR DURING SHUTING DOWN")
    
    def reboot(self):
        try:
            for vm in self.pool:
                vm.status.reboot.post()
                print(f"VM {vm['vmid']} REBOOTED")
        except:
            print("ERROR DURING REBOOTING DOWN")
    
    