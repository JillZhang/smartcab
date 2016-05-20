import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.previous_reward = 0
        self.previous_action = None
        self.success=0
        
        #stats about the algorithm
        self.success=0
        self.steps=0
        self.fail=0
        self.total=0
        self.moves=0
    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.previous_reward = 0
        self.steps=0
        self.previous_action = None
        self.policy = None
        
    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        inputs['waypoint']=self.next_waypoint
        self.state=inputs
        
        # TODO: Select action according to your policy
        possible_actions=[]
        if self.state['light']=='red':
            if self.state['oncoming']!='left':
                possible_actions=['right',None]
            else:
                possible_actions=[None]
        else:
            if self.state['oncoming']=='forward':
                possible_actions=['right','forward']
            else:
                possible_actions=['right','forward','left']
        
        if self.policy==None:
            action = random.choice(possible_actions)
        else:
            if 'forward' in possible_actions:
                action='forward'
            else:
                action=None

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        if reward>self.previous_reward:
            self.policy='continue'
        else:
            self.policy=None
        '''   
        self.previous_reward=reward
        if self.done==True:
            self.success+=1
        '''
        self.moves+=1
        self.steps+=1
        add_total = False
        if deadline == 0:
            add_total = True
        if reward >5:
            self.success += 1
            add_total = True
        if reward<0:
            self.fail+=1
        if add_total:
            self.total += 1
            print "success={},steps={},penalty_rate={},total={}".format(self.success,self.steps,round(float(self.fail)/float(self.moves), 2),self.total)
        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track

    # Now simulate it
    sim = Simulator(e, update_delay=0.0000001)  # reduce update_delay to speed up simulation
    sim.run(n_trials=100)  # press Esc or close pygame window to quit


if __name__ == '__main__':
    run()
