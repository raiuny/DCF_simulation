from abc import ABC, abstractmethod
from collections import Counter
from typing import List
class Node(ABC):
    # def __init__(self, lambda_i, t0, id) -> None:
    #     super().__init__()
    @abstractmethod
    def updateBy(self):
        pass

class Link(ABC):
    @abstractmethod
    def get_state(self):
        pass
    
    @property
    def request_list(self):
        # only one can be sent 
        pass 
    
class Env:
    def __init__(self, rt) -> None:
        self.rt = rt # 模拟时间长: 有rt个time slot
        self.clock = 0 # 初始化环境时钟
        self.timespan = [0]*rt # time slots 
        self.nodes = None
        self.links = None
        
    def add_nodes(self, nodelist: List[Node]):
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
            for node in self.nodes:
                signal = node.updateBy(channel_states) # 表示节点打算在在第signal个link上发送数据
                if signal is not None:
                    self.links[signal].request_list.append(node.id)
            # end of the time slot:
            for l in self.links:
                if l.get_state() == -1:
                    for nid in l.request_list:
                        self.nodes[nid].collision()
                l
            for node in self.nodes:
                node.update()

                    
            
            
                    
                
                
                
     