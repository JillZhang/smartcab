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
               
        self.prev_action=None
        self.prev_state=None
        self.pre_reward=None
        
        #parameter for the Q-learning
        self.Q={}
        self.learning_rate = 0.9
        self.discount_factor = 0.2    
        self.epsilon = 0.1
        self.default_Q=20
        
        #stats about the algorithm
        self.success=0
        self.steps=0
        self.fail=0
        self.total=0
        self.moves=0
    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.prev_action=None
        self.prev_state=None     
        self.pre_reward=None
        self.steps=0
    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        inputs['waypoint']=self.next_waypoint
        del inputs['left']
        del inputs['right']     
 
        state=tuple(inputs.values())


        # TODO: Select action according to your policy
        valid_actions=['left','right','forward',None]
        best_action=None
        if random.random()<=self.epsilon:
            best_action=random.choice(valid_actions)
            if (state,best_action) not in self.Q.keys():
                self.Q[(state,best_action)]=self.default_Q
            Q_value=self.Q[(state,best_action)]
        else:
            self.best_Q=-99999999
            for action in valid_actions:
                if (state,action) not in self.Q.keys():
                    self.Q[(state,action)]=self.default_Q
                Q_value=self.Q[(state,action)]
                if Q_value>self.best_Q:
                    self.best_Q=Q_value
                    best_action=action
                if Q_value==self.best_Q:
                    best_action=random.choice([best_action,action])
                
        action=best_action
        # Execute action and get reward
        reward = self.env.act(self, action)
        
        # TODO: Learn policy based on state, action, reward
        if self.prev_state!=None:
            self.Q[(self.prev_state,self.prev_action)] = (1 - self.learning_rate)*self.Q[(self.prev_state,self.prev_action)]+\
            self.learning_rate * (self.pre_reward + self.discount_factor * self.Q[(state,action)])
                    
        self.prev_state=state
        self.pre_reward=reward
        self.prev_action=action
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
        
        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action,reward)# [debug]


def run():
    """Run the agent for a finite number of trials."""
    trials = 100
    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track

    # Now simulate it
    sim = Simulator(e, update_delay=0.000001)  # reduce update_delay to speed up simulation
    sim.run(n_trials=trials)  # press Esc or close pygame window to quit


if __name__ == '__main__':
    run()
