      
import numpy as np
from scipy.optimize import root_scalar
import matplotlib.pyplot as plt

def p_func(p, n, w, k):
    if k == np.inf:
        p_fn = p - np.exp((-2 * n) * (2 * p - 1) / (p * w))
    else:
        p_fn = p - np.exp((-2 * n) * (2 * p - 1) / ( (2 * p - 1) + w * (p - 2 ** k * (1 - p) ** (k + 1))))
    return p_fn

def dcf_ana(n, w, k, lp, r):
    slot_time = 9
    basic_rate = 24
    phy_preamble = 20
    sifs = 16
    difs = 34

    ack_size_bits = 14 * 8
    data_size_bits = lp
    guard_interval = 0.8
    symbol_duration = 12.8 + guard_interval
    phy_preamble_and_header = 48
    symbol_duration_ack = 4
    service_field_length = 16
    tail_length = 6
    mac_header_size = (30) * 8
    app_header_size = 8 * 8

    data_bits_per_symbol = r * symbol_duration
    num_symbols = np.ceil((service_field_length + mac_header_size + data_size_bits + app_header_size + tail_length) / data_bits_per_symbol)
    t_data = phy_preamble_and_header + (symbol_duration * num_symbols)
    data_bits_per_ack_symbol = basic_rate * symbol_duration_ack
    num_ack_symbols = np.ceil((service_field_length + ack_size_bits + tail_length) / data_bits_per_ack_symbol)
    t_ack = phy_preamble + (symbol_duration_ack * num_ack_symbols)
    tt = (t_data + sifs + t_ack + difs) / slot_time
    tf = (t_data + difs) / slot_time

    root_result = root_scalar(p_func, args=(n, w, k), bracket=[0.00001, 0.99999], method='brentq')
    pa = root_result.root

    a = 1 / (1 + tf - tf * pa - (tt - tf) * pa * np.log(pa))

    tp = 2 * a * pa * (2 * pa - 1) * tt / (w * (pa - 2 ** k * (1 - pa) ** (k + 1)))
    nr = tp * lp / (slot_time * tt)
    dy = tt / tp

    return nr, dy, pa, a


# main function begins here
if __name__ == '__main__':
    n = [5, 10, 15, 20]
    analysis_tpts= []
    delays = []
    for num in n:
        nr, dy, pa, a = dcf_ana(num, 16, 6, 1500*8, 77.4)
        nr = nr * num
        analysis_tpts.append(nr)
        delays.append(dy/1000)
    
    #Bianchi Throughput
    bianchi_tpt = [32.97330709, 31.12632959, 29.94046185, 29.0621178]
    #ns-3 results
    thpt = [32.8871, 31.284, 29.9644, 29.061]
    #HOL delay in ms
    hol_delay1 = [1.82, 3.85, 6.02, 8.23]
    hol_delay2 = [1.52, 3.55, 5.72, 7.93]
    print("Relative Error, Analysis: ", (np.array(analysis_tpts) - np.array(thpt))/np.array(analysis_tpts))
    print("Relative Error, Bianchi: ", (np.array(bianchi_tpt) - np.array(thpt))/np.array(bianchi_tpt))
    plt.plot(n, analysis_tpts, label='Analytical')
    plt.plot(n, bianchi_tpt, label='Bianchi')
    plt.scatter(n, thpt, label='ns-3')
    plt.legend()
    plt.xlabel('Number of stations')
    plt.ylabel('Throughput (Mbps)')
    plt.savefig('thpt.png')

# ns-3 commands
# ./ns3 run "wifi-eht-network  --phyMode=EhtMcs6 --pktSize=1500  --duration=10 --networkSize=5 --gi=800 --channelWidth=20 --frequency2=0 --frequency3=0 --pktInterval=100"
# ./ns3 run "wifi-eht-network  --phyMode=EhtMcs6 --pktSize=1500  --duration=10 --networkSize=10 --gi=800 --channelWidth=20 --frequency2=0 --frequency3=0 --pktInterval=100"
# ./ns3 run "wifi-eht-network  --phyMode=EhtMcs6 --pktSize=1500  --duration=10 --networkSize=15 --gi=800 --channelWidth=20 --frequency2=0 --frequency3=0 --pktInterval=100"
# ./ns3 run "wifi-eht-network  --phyMode=EhtMcs6 --pktSize=1500  --duration=100 --networkSize=20 --gi=800 --channelWidth=20 --frequency2=0 --frequency3=0 --pktInterval=100"

    