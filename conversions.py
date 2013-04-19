'''
Conversion definitions
'''
architectures = { 'i386' : '32', '32' : 'i386', 'x86_64' : '64', '64' : 'x86_64' }
root_device_types = { 'ebs' : 'ebs', 'instance-store' : 's3', 's3' : 'instance-store' }
virt_types = { 'hvm' : 'hvm', 'paravirtual' : 'pv', 'pv' : 'paravirtual' }