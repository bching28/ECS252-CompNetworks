import random
import simpy
import math
import time

RANDOM_SEED = 29
SIM_TIME = 100000
NUM_HOSTS = 10
SLOT_TIME = 1

class stats:
    def __init__(self):
        self.successful_slots = 0
        self.total_slots = 0
        self.num_collisions = 0
        self.wasted_slots = 0

    def throughput(self):
        throughput = float(self.successful_slots)/self.total_slots
        print 'Throughput:', throughput

class node:
    def __init__(self, env, arrival_rate):
        self.env = env
        self.arrival_rate = arrival_rate
        self.N = 0 # num of retransmission times
        self.S = 0 # slot num of next transmission
        self.L = 0 # num of pkts in queue
        self.server = simpy.Resource(env, capacity = 1)

    def process_packet(self, env):
        with self.server.request() as req:
            yield req
            self.L -= 1
            self.N = 0
            self.S += 1

    def packets_arrival(self, env):
        # Infinite loop for generating packets
        while True:
            yield env.timeout(random.expovariate(self.arrival_rate))
            # infinite buffer
            self.L += 1 # creating new packet and adding to queue
            #env.process(self.process_packet(env, new_packet)) # you don't process packet until empty slot


    # implement binary exponential backoff
    def binary_exp_backoff(self):
        # increment retransmission attempts
        self.N += 1

        # perform binary exponential backoff computation
        K = min(self.N, 10)
        r = random.randint(0, (2**K)+1)
        self.S += r

    def linear_backoff(self):
        # increment retransmission attempts
        self.N += 1

        # perform linear backoff computation
        K = min(self.N, 1024)
        r = random.randint(0, K+1)
        self.S += r

class server:
    def __init__(self, env, arrival_rate, list_of_hosts, backoff_algorithm, statistics):
        self.env = env
        self.arrival_rate = arrival_rate
        self.list_of_hosts = list_of_hosts
        self.backoff_algorithm = backoff_algorithm
        self.statistics = statistics
        self.curr_slot_number = 0 # also the total number of slots

    def run(self):
        yield self.env.timeout(100) # yield time for packets to initially arrive
        while True:
            yield self.env.timeout(SLOT_TIME) # yield periodically to make up every slot time
            num_transmissions = 0 # number of transmission at any given time

            # check for simultaneous packet transmissions (i.e. if it is time for host to send)
            # check if host's queue has packets
            transmitting_hosts = []
            for h in range(NUM_HOSTS):
                if (self.list_of_hosts[h].L > 0 and self.list_of_hosts[h].S == self.curr_slot_number):
                    transmitting_hosts.append(h)
                    num_transmissions += 1

            # if only one host is transmitting, then use that index
            if len(transmitting_hosts) == 1:
                one_active_host_index = transmitting_hosts[0]

            if num_transmissions == 1: # no collisions
                self.statistics.successful_slots += 1
                self.env.process(self.list_of_hosts[one_active_host_index].process_packet(self.env))
            elif num_transmissions > 1: # collisions
                self.statistics.num_collisions += 1
                for h in transmitting_hosts:
                    if self.backoff_algorithm == 'binary exponential':
                        self.list_of_hosts[h].binary_exp_backoff()
                    elif self.backoff_algorithm == 'linear':
                        self.list_of_hosts[h].linear_backoff()
            else: # num_transmissions < 1; wasted slot
                self.statistics.wasted_slots += 1

            self.curr_slot_number += 1 # increment slots for each iteration
            self.statistics.total_slots = self.curr_slot_number

            # for hosts that don't transmit, update their next transmission attempt
            # helps with when L=0 at the start of the simulation
            for h in range(NUM_HOSTS):
                if ((h not in transmitting_hosts) and (self.list_of_hosts[h].S < self.curr_slot_number)):
                    self.list_of_hosts[h].S = self.curr_slot_number

def main():
    # lambda = [0.01 ... 0.09] with step size of 0.01
    for algorithm in ['binary exponential', 'linear']:
        print 'Performing', algorithm, 'backoff algorithm'
        for arrival_rate in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]:
            statistics = stats()
            env = simpy.Environment()
            list_of_hosts = []

            # initializing hosts
            for h in range(NUM_HOSTS):
                list_of_hosts.append(node(env, arrival_rate))

            # have packets arrive simultaneously
            for h in range(NUM_HOSTS):
                env.process(list_of_hosts[h].packets_arrival(env))

            backoff_algorithm = algorithm
            router = server(env, arrival_rate, list_of_hosts, backoff_algorithm, statistics)
            env.process(router.run())
            env.run(until=SIM_TIME)
            statistics.throughput()


if __name__ == '__main__':
    main()
