

class BMSSettings():
    ports = [['22', 2222], ['8787', 8787]]
    
    device = ["/dev/fuse"]

    capabilities = ["SYS_ADMIN", "DAC_READ_SEARCH"]

    image = 'docker.rdcloud.bms.com:443/rr:Genomics2019-03_base'

