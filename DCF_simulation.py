import numpy as np
from numpy.random import rand, randint, choice
from typing import List, SupportsIndex
from collections import deque
from math import pow
# from environment import Node, Env
# global variables
class Clock:
    def __init__(self, begin = 0) -> None:
        self._time = begin
        self.observers = []
    
    def add_observers(self, obs):
        for o in obs:
            self.observers.append(o)
    
    @property
    def time(self):
        return self._time
    
    def update(self):
        self.time += 1
    
    @time.setter
    def time(self):
        for obs in self.observers:
            obs.log()  
        
rt = 10000
q = 0.5
W = 4
K = 5
t0 = 5 # holding time of HOL packets in successful transmission
f0 = 2 # holding time of HOL packets in collision

global_clock = Clock()

class Station:
    def __init__(self, lambda_i, t0, f0, id) -> None:
        self.id = id   
        self.t0 = t0 # holding time of HOL packets in successful transmission
        self.f0 = f0
        self.lambda_i = lambda_i
        self.packets: List[Packet] = []
        self.clock = global_clock # 使用全局时钟
        # 节点记录保存
        self.acdelays = [] 
        self.second_acdelays = []
        self.slog = []
        self.coln = 0 # 未碰撞状态

    @property
    def HOLpacket(self):
        if len(self.packets):
            return self.packets[0]
        else:
            return None
    
    @property
    def state(self):
        if self.HOLpacket is not None:
            return self.HOLpacket.state
        return 0
    
    def collision(self):
        self.coln = 1 # 发生碰撞
        self.HOLpacket.update_ri() # 发生碰撞时候会延迟更新HOL包的ri状态
        self.HOLpacket.update_bcnt()

    def checkin(self): # begin of the slot time
        # check HOLpacket finish
        if self.HOLpacket is not None:
            if self.HOLpacket.state == 1: # HOLpacket有三种状态： 0: 等待发送bcnt!=0; 1: 正在发送bcnt=0, 持续t0时间;-1: 碰撞bcnt=0, 持续f0时间
                if self.HOLpacket.finished:
                    self.acdelays.append(self.HOLpacket.calc_acdelay())
                    self.packets.pop(0)
                else:
                    self.HOLpacket_1_delay_task()
            elif self.HOLpacket.state == -1:
                self.HOLpacket_minus1_delay_task()
            else: # 空闲状态
                self.HOLpacket.update_bcnt()
        if rand() < self.lambda_i: # one packet comes
            self.packets.append(Packet(self.t0, self.f0, self.clock.time))  
            
    def channel_id_rts_by(self, channel_states) -> SupportsIndex: # HOL包的状态用节点状态表示，调用update函数进行状态更新
        if self.state:
            return None
        if self.HOLpacket is None:
            return None
        idle_channels = []
        for c, s in enumerate(channel_states):
            if not s: # 如果未被占用
                idle_channels.append(c)
        if len(idle_channels) > 0:
            if self.HOLpacket.bcnt == 0:
                return choice(idle_channels)
        return None
    
    def HOLpacket_1_delay_task(self):
        if self.clock.time - self.HOLpacket.serve_time + 1== t0:
            self.acdelays.append(self.HOLpacket.calc_acdelay())
            self.packets.pop(0)
    
    def HOLpacket_minus1_delay_task(self):
        if self.clock.time - self.HOLpacket.clnt + 1== f0:
            self.HOLpacket.update_ri()
            self.HOLpacket.update_bcnt()
    
    def log(self):
        self.slog.append(self.state)
        
            


    
class Packet:
    def __init__(self, t0, f0, tim) -> None:
        self.t0 = t0
        self.f0 = f0
        self.arrive_time = tim # arrive time
        self.ri = 0
        self.bcnt = randint(0,self.mwin) # 初始化back_count
        self._serve_time = None
        self._finished = False
        self.colncnt = 0
        self.colnt = 0
        
    @property
    def mwin(self):
        return np.ceil(W*pow(1/q, min(self.ri, K))-1)

    @property
    def isready(self):
        return self.bcnt == 0
    
    @property
    def state(self):
        if self.bcnt == 0 and self.serve_time is not None:
            return 1
        elif self.colncnt:
            return -1
        return 0 # 等待
    
    @property
    def serve_time(self):
        return self._serve_time
    
    @serve_time.setter
    def serve_time(self, new_time):
        self._serve_time = new_time
        print(f"HOL packet begin to send at {self._serve_time}")
        
    def collision(self):
        if self.colncnt == 0:
            self.colnt = global_clock.time
        self.colncnt = (self.colncnt + 1)%f0
        
    def update_ri(self):
        self.ri += 1
        
    def update_bcnt(self):
        if self.bcnt:
            self.bcnt -= 1
        else:
            self.bcnt = randint(0, self.mwin)
        
    def calc_acdelay(self):
        if self.serve_time is not None:
            return self.serve_time - self.arrive_time
        else:
            return None
    
    def finish(self):
        self._finished = True
    
    @property
    def finished(self):
        return self._finished
    

            
        
class Link: # 三种状态：占用；空闲；冲突
    def __init__(self, id) -> None:
        self.clock = global_clock
        self.id = id
        self.user_id = None # 使用的站点
        self.user: Packet = None # HOL包的引用
        # 链路状态记录
        self.rlist = [] # request_list
        self.slog = []
        self.state = 0 # 空闲
        self.colncnt = 0

    def __str__(self) -> str:
        return f"id: {self.id}, states: {self.slog}"
    
    def add_request(self, nid):
        if self.state == 0:
            self.rlist.append(nid)
            return True
        return False  
    
    def collision(self):
        self.state = -1
        self.colncnt += 1
        if self.colncnt == f0:
            self.colncnt = 0
            self.state = 0

        
    def clear_request(self):
        self.rlist = []
        if self.state == -1:
            self.state = 0
        
    def check_packet_time(self):
        if self.user is not None:
            if self.user.t0 == self.clock.get_time() - self.serve_at + 1: # done 
                self.user.finish()
                self.user = None # unload
                self.user_id = None
                self.state = 0
                self.rlist = []
            
    def get_state(self):
        return len(self.rlist) # >1表示被占用，0表示空闲, 1表示成功传输
    
    def load(self, packet: Packet, nid):
        if self.state == 0:
            assert packet is not None, "packet is None!"
            self.user = packet
            self.user_id = nid
            self.serve_at = self.clock.get_time()
            # 更新HOLpacket接受服务的时间
            self.user.serve_time = self.serve_at
            self.state = 1
    
    def log(self):
        self.slog.append(self.state)
        
     
        
class Env:
    def __init__(self, rt) -> None:
        self.rt = rt # 模拟时间长: 有rt个time slot
        self.timespan = [0]*rt # time slots  
        self.nodes: List[Station] = None
        self.links: List[Link] = None
        
    def add_nodes(self, nodelist: List[Station]):
        self.nodes = nodelist
    
    def add_links(self, linklist: List[Link]):
        self.links = linklist
        self.link_states = [0]*len(linklist)
        
    def run_simulation(self):
        for t in range(self.rt):
            # begin of the time slot:
            channel_states = []
            for l in self.links:
                channel_states.append(l.get_state())
            print(f"time slot {t}")
            for node in self.nodes:
                node.checkin()
                print(f"{node.id}: packets_len: {len(node.packets)}")
                if len(node.packets):
                    print(f"packets_bcnt: {node.HOLpacket.bcnt}")
                signal = node.channel_id_rts_by(channel_states) # 表示节点打算在在第signal个link上发送数据
                print(signal)
                if signal is not None:
                    self.links[signal].add_request(node.id)
            # mid of the time slot: 检查每个链路，如果这条链路正在传输，busy状态，则更新传输包的age; 如果这条链路请求冲突，则对每个冲突节点发送重传消息，让他们更新窗口大小
            for l in self.links:
                ret = l.get_state() # 返回申请的个数
                if ret:
                    if ret > 1: # 发生冲突
                        for nid in l.rlist:
                            self.nodes[nid].collision()
                        l.collision()
                    else: # 成功传输
                        l.load(self.nodes[l.rlist[0]].HOLpacket, ret)
                        l.success()
                l.check_packet_time() # 看是否传输成功
            
            # end of the time slot: update clock
            global_clock.update()

if __name__ == "__main__":
    # create stations
    stations = []
    for i in range(3):
        stations.append(Station(
            lambda_i=0.5,
            t0=5,
            f0=2,
            id=i
        ))
    # create links
    links = []
    for i in range(2):
        links.append(Link(id=i))
    global_clock.add_observers(stations)
    global_clock.add_observers(links)
    env = Env(rt=100000)
    env.add_nodes(stations)
    env.add_links(links)
    env.run_simulation()