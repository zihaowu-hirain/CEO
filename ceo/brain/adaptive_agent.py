import random
import datetime
from typing import Callable, override

from langchain_core.language_models import BaseChatModel

from ceo.brain.agent import Agent


class AdaptiveAgent(Agent):
    def __init__(self, abilities: list[Callable],
                 brain: BaseChatModel, name: str,
                 p: float, beta: float, query: str = ''):
        super().__init__(abilities=abilities, brain=brain, name=name, query=query)
        self.memory = dict()  # json
        self.expected_step = 0
        self.p = p  # (0, 1)
        self.beta = beta  # (0, MAX)
        self.__origin_p = p

    @override
    def reposition(self):
        super().reposition()
        self.memory = dict()
        self.expected_step = 0
        self.p = self.__origin_p
        return self

    @override
    def assign(self, query: str):
        super().assign(query)
        self.reposition()

    @override
    def reassign(self, query: str):
        return self.assign(query)

    def estimate_step(self):
        if self.query_by_step == '':
            self.expected_step = 0
            return
        self.plan()
        self.expected_step = len(self.schedule)

    def memorize(self, action_performed: str):
        now = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S.%f')
        self.memory[f"Agent {self.name} at {now}"] = {
            'time': now,
            'action_performed': action_performed
        }

    def stop(self) -> bool:
        if random.uniform(0, 1) > self.p:
            return False
        return True

    def punish(self):
        self.p = (self.beta * self.p) % 1.0

    @override
    def step_quiet(self) -> str:
        pass

    @override
    def just_do_it(self) -> str | None:
        return


'''
算法：
        维护一个局部记忆池，每个步骤需要有自己的时间戳
        首先使用LLM预估一个预期步骤数
        达到步骤数阈值后，每一个步骤都以 p (0-1) 的惩罚概率进行惩罚，以p-1的概率继续，以p概率停止
        维护一个惩罚系数 beta (>0)，超出预期步骤的每一次执行，都会将惩罚概率更新为 (beta * p) % 1
        维护当前任务详细内容
        
        1. 结合记忆池和当前任务目标，思考并分析是否需要或是否有能力进行下一步
            1.1 如果没有进行下一步，则任务结束，此时判断任务达成与否
        2. 如果需要进行下一步，则思考当前需要调动哪个能力（一次仅执行一个动作）
        (重复以上过程，直到 2. 中决定退出)
'''