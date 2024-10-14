from proxmoxer import ProxmoxAPI
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename="example.log", encoding="utf-8", level=logging.INFO)


def nodes(ip, username, password):
    proxmox = ProxmoxAPI(
        ip, user=username, password=password, verify_ssl=False, service="PVE"
    )
    return proxmox.nodes.get()


def connect(vmids, ip, username, password, node):
    try:
        proxmox = ProxmoxAPI(
            ip, user=username, password=password, verify_ssl=False, service="PVE"
        )
        node = proxmox.nodes([node])
        pool = list(map(int, vmids.split(",")))
        vms = []
        for elem in node.qemu.get():
            if elem["vmid"] in pool:
                vms.append((node.qemu(elem["vmid"]), elem))
        return vms
    except:
        logger.error("CONNECTION ERROR")


def create(ip, username, password, node, golden_img, count):
    proxmox = ProxmoxAPI(
        ip, user=username, password=password, verify_ssl=False, service="PVE"
    )
    node = proxmox.nodes([node])
    max_vmid = 1 + max([vm["vmid"] for vm in node.qemu.get()])
    gi = node.qemu(golden_img)
    for i in range(max_vmid, max_vmid + count):
        gi.clone.post(newid=i)
    return [str(i) for i in range(max_vmid, max_vmid + count)]


def checkPool(vmids, ip, username, password, node):
    pool = connect(vmids, ip, username, password, node)
    cpu = 0
    mem = 0
    for vm in pool:
        vm = vm[0].config().get()
        cpu += vm["cores"] * vm["sockets"]
        mem += int(vm["memory"])
    return cpu, mem


def getPool(vmids, ip, username, password, node):
    pool = connect(vmids, ip, username, password, node)
    info = []
    for vm in pool:
        info.append((vm[0].config().get(), vm[1]))
    return info


def delete(vmids, ip, username, password, node):
    try:
        pool = connect(vmids, ip, username, password, node)
        for vm in pool:
            vm[0].delete()
    except:
        logger.error("ERROR DURING DELETE")


def stop(vmids, ip, username, password, node):
    pool = connect(vmids, ip, username, password, node)
    try:
        for vm in pool:
            vm[0].status.stop.post()
    except:
        logger.error("ERROR DURING STOPING POOL")


def start(vmids, ip, username, password, node):
    pool = connect(vmids, ip, username, password, node)
    try:
        for vm in pool:
            vm[0].status.start.post()
    except:
        logger.error("ERROR DURING STARTING POOL")


def shutdown(vmids, ip, username, password, node):
    pool = connect(vmids, ip, username, password, node)
    try:
        for vm in pool:
            vm[0].status.shutdown.post()
    except:
        logger.error("ERROR DURING SHUTING DOWN")


def reboot(vmids, ip, username, password, node):
    pool = connect(vmids, ip, username, password, node)
    try:
        for vm in pool:
            vm[0].status.reboot.post()
    except:
        logger.error("ERROR DURING REBOOTING DOWN")
