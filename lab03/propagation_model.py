#!/usr/bin/python

'This example creates a simple network topology with 1 AP and 3 stations'

from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.cli import CLI
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference

import matplotlib.pyplot as plt

def topology():
    "Create a network."
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference)

    info("*** Creating nodes\n")
    net.addStation('sta1', position='10,20,0')
    net.addStation('sta2', position=f"30,20,0")
    net.addStation('sta3', position='60,20,0')
    net.addAccessPoint('ap1', ssid="my-ssid", mode="a", channel="36",
                       failMode='standalone', position='10,10,0')

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="friis")

    # net.plotGraph(max_x=1000, max_y=1000)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Starting network\n")
    net.build()

    # info("*** Running CLI\n")
    # CLI(net)

    return net

def main():
    setLogLevel('info')
    distances = []
    bandwidths = []
    signal_strengths = []
    net = topology()
    sta1, sta2 = net.get("sta1", "sta2")
    info("*** Starting benchmarks ***\n")
    try:
        for distance in range(0, 2000, 100):
            info(f"*** Distance between sta1 and sta2: {distance}\n")
            sta2.setPosition(f"{10 + distance},20,0")
            results = net.iperf((sta1, sta2))
            signal_strength = float(sta2.cmd("iw dev sta2-wlan0 link | grep signal").strip().split("signal:")[1].strip()[0:3])
            bw1 = float(results[0].split(" ")[0])
            bw2 = float(results[1].split(" ")[0])
            bandwidth = 0.5 * (bw1 + bw2)
            print(bandwidth)
            print(signal_strength)
            distances.append(distance)
            bandwidths.append(bandwidth)
            signal_strengths.append(signal_strength)
    except Exception as e:
        info(f"error: {e}")
        info("*** Stopping network\n")
        net.stop()
        return

    info("*** Stopping network\n")
    net.stop()

    fig, ax1 = plt.subplots()

    color = 'tab:blue'
    ax1.set_xlabel('distance (m)')
    ax1.set_ylabel('RSS (dBm)')
    ax1.plot(distances, signal_strengths, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    color = 'tab:red'
    ax2 = ax1.twinx()
    ax2.set_ylabel('throughput (Mbits/s)', color=color)
    ax2.plot(distances, bandwidths, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()
    info("*** Plotting results\n")
    plt.show()

if __name__ == '__main__':
    main()
