from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import csv

# Function to connect to vCenter server
def connect_to_vcenter(host, username, password):
    try:
        si = SmartConnect(
            host=host,
            user=username,
            pwd=password,
            port=443
        )
        return si
    except Exception as e:
        print("Failed to connect to vCenter server:", str(e))
        return None

# Function to disconnect from vCenter server
def disconnect_from_vcenter(si):
    if si:
        Disconnect(si)

# Function to get all virtual machines
def get_all_vms(si):
    content = si.RetrieveContent()
    container = content.viewManager.CreateContainerView(
        content.rootFolder,
        [vim.VirtualMachine],
        True
    )
    vms = container.view
    container.Destroy()
    return vms

# Function to get VM details (CPU, Memory, Storage)
def get_vm_details(vm):
    return {
        "Name": vm.name,
        "CPU": vm.summary.config.numCpu,
        "Memory (GB)": vm.summary.config.memorySizeMB / 1024,
        "Storage (GB)": sum([disk.capacityInBytes for disk in vm.config.hardware.device if isinstance(disk, vim.VirtualDisk)]) / (1024**3)
    }

# Function to calculate VM utilization score
def calculate_utilization_score(vm):
    cpu_usage = vm.summary.quickStats.overallCpuUsage
    memory_usage = vm.summary.quickStats.guestMemoryUsage
    cpu_allocated = vm.summary.config.numCpu
    memory_allocated = vm.summary.config.memorySizeMB / 1024

    cpu_utilization_score = cpu_usage / cpu_allocated
    memory_utilization_score = memory_usage / memory_allocated

    return {
        "CPU Utilization Score": cpu_utilization_score,
        "Memory Utilization Score": memory_utilization_score
    }

# Function to analyze VMs and generate recommendations
def analyze_vms(vms):
    recommendations = []
    for vm in vms:
        vm_details = get_vm_details(vm)
        utilization_scores = calculate_utilization_score(vm)

        if utilization_scores["CPU Utilization Score"] > 0.8:
            recommendations.append({
                "VM Name": vm_details["Name"],
                "Recommendation": "Oversize - High CPU utilization"
            })
        elif utilization_scores["Memory Utilization Score"] > 0.8:
            recommendations.append({
                "VM Name": vm_details["Name"],
                "Recommendation": "Oversize - High memory utilization"
            })
        elif utilization_scores["CPU Utilization Score"] < 0.2:
            recommendations.append({
                "VM Name": vm_details["Name"],
                "Recommendation": "Undersize - Low CPU utilization"
            })
        elif utilization_scores["Memory Utilization Score"] < 0.2:
            recommendations.append({
                "VM Name": vm_details["Name"],
                "Recommendation": "Undersize - Low memory utilization"
            })

    return recommendations

# Function to write VMs and recommendations to a CSV file
def write_to_csv(vms, recommendations, csv_file):
    with open(csv_file, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames
