import random
import simpy
import math

RANDOM_SEED = 29
SIM_TIME = 1000000
NUM_HOSTS = 10
SLOT_TIME = 1

class node:
    def __init__(self, env):
        self.env = env
        self.N = 0 # num of retransmission times
        self.S = 0 # slot num of next transmission
        self.L = 0 # num of pkts in queue

    def update(): # update n and s

	def process_packet(self, env, packet):
		with self.server.request() as req:
			start = env.now
			yield req
			yield env.timeout(random.expovariate(MU))
			latency = env.now - packet.arrival_time
			#self.Packet_Delay.addNumber(latency)
			self.L -= 1
			if self.L == 0:
				self.flag_processing = 0
				self.start_idle_time = env.now
            self.N = 0
            self.S += 1

	def packets_arrival(self, env):
	    while True:
	         # Infinite loop for generating packets
		    yield env.timeout(random.expovariate(self.arrival_rate))
		    self.packet_number += 1
		    arrival_time = env.now  
		    new_packet = Packet(self.packet_number,arrival_time)
		    if self.flag_processing == 0:
			    self.flag_processing = 1
			    idle_period = env.now - self.start_idle_time
			    self.Server_Idle_Periods.addNumber(idle_period)
		    self.L += 1
		    env.process(self.process_packet(env, new_packet))

    def run():
        # starve arrivals
        # wait a period of time for arrivals

class server:
    def __init__(self, env, arrival_rate, backoff_algorithm):
        self.env = env
        self.arrival_rate = arrival_rate
        self.backoff_algorithm = backoff_algorithm
        self.list_of_hosts = []
    
    def run():
        for h in NUM_HOSTS:
            self.list_of_hosts.append(node(self.env)) # initializing hosts

        # have packets arrive simultaneously
        for h in NUM_HOSTS:
            arrive = self.list_of_hosts[h].packets_arrival(self.env)
            self.env.process(arrive)
        
        while True:
            yield self.env.timeout(SLOT_TIME) # yield periodically to make up every slot time
            num_transmissions = 0
            
            # check for simultaneous packet transmissions
            # check if host's queue has packets
            for h in NUM_HOSTS:
                if self.list_of_hosts[h].L > 0:
                    num_transmissions += 1
                    active_host_index = h

            if num_transmissions == 1: # no collisions
            elif num_transmissions > 1: # collisions
            else: # num_transmissions < 1; wasted slot



        # implement binary exponential backoff

def main():
    # lambda = [0.01 ... 0.09] with step size of 0.01
    for arrival_rate in range(0.01, 0.09, 0.01):
        env = simpy.Environment()
        router = server(env, arrival_rate, backoff_algorithm)
		env.process(router.run())
		env.run(until=SIM_TIME)



if __name__ == '__main__':
    main()
