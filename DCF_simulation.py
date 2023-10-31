import numpy as np
from numpy.random import rand
from typing import List
from collections import deque
from math import pow
# global variables
rt = 10000
q = 0.5
W = 4
K = 5
t0 = 16 # holding time of HOL packets in successful transmission
f0 = 10 # holding time of HOL packets in collision

class Node:
    def __init__(self, lambda_i, t0, id) -> None:
        self.id = id   
        self.t0 = t0 # holding time of HOL packets in successful transmission
        self.lambda_i = lambda_i
        self.packets: List[Packet] = []
        self.HOLpacket: HOLPacket = None
        self.clock = 0 # 初始化节点时钟
        
        # 节点记录保存
        self.acdelays = [] 
        self.second_acdelays = []
 
            
    def checkin(self): # begin of the slot time
        self.clock = self.clock + 1
        if rand() < self.lambda_i: # one packet comes
            self.packets.append(Packet(self.t0, f0, self.clock))
            
    def update(self, channel_state): # HOL包的状态用节点状态表示，调用update函数进行状态更新
        if channel_state == 0: # idle
            if len(self.packets) != 0:
                self.state = 1
            else:
                self.state = -1
                
    def tosend(self): # when the channel is idle, this function will be called
        if self.back_cnt == 0:
            return 1
        else:
            self.back_cnt = self.back_cnt - 1 
            return 0
        
    def send(self):
        self.sending_pkt = self.packets.popleft()
        self.sending_pkt.sendat(self.clock)
        
    
class Packet:
    def __init__(self, t0, f0, tim) -> None:
        self.t0 = t0
        self.f0 = f0
        self.at = tim # arrive time
        
    def sendat(self, tim):
        self.st = tim # time to send
        delay = self.st - self.at
        return delay
    
    def __del__(self):
        print("Packet sended!")
        
class HOLPacket:
    def __init__(self, p: Packet) -> None:
        self.pkt = p
        self.state = 1 # 0: T  1: R  2: F 
        self.ri = 0
        self.back_count = np.floor(rand()*self.mwin)

    @property
    def mwin(self):
        return np.ceil(W*pow(1/q, min(self.ri, K))-1)

    def update(self, signal):
        if signal == 0: # 信道空闲
            if self.back_count == 0:
                ... #尝试发送
            self.back_count -= 1

            
        
class Link:
    def __init__(self, st = 0) -> None:
        self.state = 0 # 0: idle 1: busy, 2: collision 
        self.clock = 0
        self.service_time = st
        if st:
            self.packets = []
        # 链路状态记录
        self.los = [] # log of states
        
    def update(self): 
        self.clock += 1

    
class env:
    def __init__(self, rt, n, lambda_a) -> None:
        self.lambda_a = lambda_a # 聚合到达率
        self.rt = rt # 模拟时间长: 有rt个time slot
        self.clock = 0 # 初始化环境时钟
        self.state = 0 # 0: idle, 1: busy, 2: collision
        self.timespan = [0]*rt # time slots 
        self.add_nodes(n)
        self.transmit_cnt = 0 # 传输时候用于计数的，当发生冲突时计数器计到f0时候置为0; 成功传输则需要计到t0, 后才能置为0
        
    def add_nodes(self, n): # 添加N个节点
        lambda_i = self.lambda_a/n/t0 # 平均每个节点每个time slot到达率
        self.Nodes = [Node(lambda_i, t0, i) for i in range(n)]

    def run_simulation(self):
        for i in range(self.rt):
            # begin of the time slot: 1. 检查数据包是否到达 2. 检查链路状态  3. 根据链路状态初始化HOL包的状态or转换HOL包的状态
            for node in self.Nodes:
                node.checkin() 
                node.update(self.state)
    