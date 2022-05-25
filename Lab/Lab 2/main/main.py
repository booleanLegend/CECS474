"""template open source created by  https://github.com/thanujann/CSMA-CD-Protocol-Simulator
"""
# CSMA/CD Algorithm
import random
import math
import collections

# simulation start time set to 1000 seconds per CECS474_Lab2_CSMACD page 6
maxSimulationTime = 1000
total_num = 0

# Class that defines a Node
class Node:
	# Constructor creates a node based on distance (location) and arrival rate
    def __init__(self, location, A):
		# Creates a queue from the queue of of arrival packet random number variables 
        self.queue = collections.deque(self.generate_queue(A))
        self.location = location  # Defined as a multiple of D
        self.collisions = 0		# Collision counter
        self.wait_collisions = 0		# Waiting for collission coutner
        self.MAX_COLLISIONS = 10	# Given data

	# Method that handles a collision 
    def collision_occured(self, R):
		# Increase the counter 
        self.collisions += 1
        if self.collisions > self.MAX_COLLISIONS:
            # Drop packet and reset collisions
            return self.pop_packet()

        # Add the exponential backoff time to waiting time
        backoff_time = self.queue[0] + self.exponential_backoff_time(R, self.collisions)

		# If backoff time is greater than arrival time of node in queue, set backoff time as arrival time
        for i in range(len(self.queue)):
            if backoff_time >= self.queue[i]:
                self.queue[i] = backoff_time
            else:
                break

	# Method that resets collisions
    def successful_transmission(self):
        self.collisions = 0
        self.wait_collisions = 0

	# Method for queue of packets of arrival rate for one node
    def generate_queue(self, A):
		# Creates a packet list
        packets = []
        arrival_time_sum = 0

		# This will take a long time to get to 1000
        while arrival_time_sum <= maxSimulationTime:
            arrival_time_sum += get_exponential_random_variable(A)
			# Adds a small value to packets list
            packets.append(arrival_time_sum)
		# Returns the list
        return sorted(packets)

	# Method that waits a random amount of time and returns float
    def exponential_backoff_time(self, R, general_collisions):
        rand_num = random.random() * (pow(2, general_collisions) - 1)
        return rand_num * 512/float(R)  # 512 bit-times

	# Method that drops last packet and resets counters
    def pop_packet(self):
        self.queue.popleft()
        self.collisions = 0
        self.wait_collisions = 0

	# Non persistent method bus busy sense
    def non_persistent_bus_busy(self, R):
		# Add a time that packet is waiting to not collide 
        self.wait_collisions += 1
        if self.wait_collisions > self.MAX_COLLISIONS:
            # Drop packet and reset collisions
            return self.pop_packet()

        # Add the exponential backoff time to waiting time
        backoff_time = self.queue[0] + self.exponential_backoff_time(R, self.wait_collisions)

		# If time is more than next arrival rate of node
        for i in range(len(self.queue)):
            if backoff_time >= self.queue[i]:
				# Make time next arrival rate node
                self.queue[i] = backoff_time
            else:
                break


# Method creates exponential random variable of arrival rate
def get_exponential_random_variable(param):
    # Get random value between 0 (exclusive) and 1 (inclusive) and subtract it from 1
    uniform_random_value = 1 - random.uniform(0, 1)
	# Logarithmic function calculates random value based on arrival rate
    exponential_random_value = (-math.log(1 - uniform_random_value) / float(param))
	# Return float value
    return exponential_random_value

# Method that builds network of nodes
def build_nodes(N, A, D):
	# Makes a list of nodes
    nodes = []
    for i in range(0, N):
        nodes.append(Node(i*D, A))
    return nodes

# CSMA/CD simulator
# bool is_persistent controls whether simulation is either persistent or not
def csma_cd(N, A, R, L, D, S, is_persistent):
	# Method values sets all values to 0 to start simulation
    curr_time = 0
    transmitted_packets = 0
    successfuly_transmitted_packets = 0
	# Builds a network of nodes given number of nodes, arrival rate of node, and distance to next node
    nodes = build_nodes(N, A, D)		

	# Runs while 
    while True:

    	# Step 1: Pick the smallest time out of all the nodes
        min_node = Node(None, A)  # Some random temporary node
        min_node.queue = [float("infinity")]
        for node in nodes:
            if len(node.queue) > 0:
				# Choose smallest node between first item in min node queue or the node queue for all the nodes in node list
                min_node = min_node if min_node.queue[0] < node.queue[0] else node

        if min_node.location is None:  # Terminate if no more packets to be delivered
            break

        curr_time = min_node.queue[0]
        transmitted_packets += 1

        # Step 2: Check if collision will happen
        # Check if all other nodes except the min node will collide
        collsion_occurred_once = False
        for node in nodes:
            if node.location != min_node.location and len(node.queue) > 0:
				# Calculate distance of locations between nodes
                delta_location = abs(min_node.location - node.location)
				# Calculate propagation delay given distance and propagation speed
                t_prop = delta_location / float(S)
				# Calculate transmission speed given packet length and LAN speed
                t_trans = L/float(R)

                # Check collision
                will_collide = True if node.queue[0] <= (curr_time + t_prop) else False

                # Sense bus
                if (curr_time + t_prop) < node.queue[0] < (curr_time + t_prop + t_trans):
					# Check if simulation is persistent
                    if is_persistent is True:
						# For amount of nodes in queue 
                        for i in range(len(node.queue)):
							# Check if current time + propagation delay is less than arrival time of current node 
							# This should also be less than current time + propagation delay + transmission delay
							# Makes latter as arrival rate of node 
                            if (curr_time + t_prop) < node.queue[i] < (curr_time + t_prop + t_trans):
								# Set last check as arrival time for that node
                                node.queue[i] = (curr_time + t_prop + t_trans)
                            else:
								# Bus is empty
                                break
                    else:
                        node.non_persistent_bus_busy(R)

                if will_collide:
                    collsion_occurred_once = True
                    transmitted_packets += 1
                    node.collision_occured(R)

        # Step 3: If a collision occured then retry
        # otherwise update all nodes latest packet arrival times and proceed to the next packet
        if collsion_occurred_once is not True:  # If no collision happened
            successfuly_transmitted_packets += 1
            min_node.pop_packet()
        else:    # If a collision occurred
            min_node.collision_occured(R)

	# Calculate efficiency by calling successfully transmitted and dividing the amount of transmitted packets
    print("Efficiency", successfuly_transmitted_packets/float(transmitted_packets))
	# Calculate throughput from division of product of packet length and successfully transmitted packets
	# from current time + packet length and speed of LAN * 1,000,000 small Mbps given that time is in millionths of seconds
    print("Throughput", (L * successfuly_transmitted_packets) / float(curr_time + (L/R)) * pow(10, -6), "Mbps")
    print("")


# Run Algorithm
# N = The number of nodes/computers connected to the LAN
# A = Average packet arrival rate (packets per second)
# R = The speed of the LAN/channel/bus (in bps)
# L = Packet length (in bits)
# D = Distance between adjacent nodes on the bus/channel
# S = Propagation speed (meters/sec)
# C = Speed of Light

D = 10
C = 3 * pow(10, 8)
S = (2/float(3)) * C

# Show the efficiency and throughput of the LAN (in Mbps) (CSMA/CD Persistent)
# Starts from 20 to 100 and skips every 20 steps
for N in range(20, 101, 20):
	# Does the following list values: 7, 10, 20 packets/s
    for A in [7, 10, 20]:
        R = 1 * pow(10, 6)
        L = 1500
        print("Persistent: ", "Nodes: ", N, "Avg Packet: ", A)		# Display current values
        csma_cd(N, A, R, L, D, S, True)		# Call CSMA-CD Protocol method with persistence being true

# Show the efficiency and throughput of the LAN (in Mbps) (CSMA/CD Non-persistent)
# Starts from 20 to 100 and skips every 20 steps
for N in range(20, 101, 20):
	# Does the following list values: 7, 10, 20 packets/s
    for A in [7, 10, 20]:
        R = 1 * pow(10, 6)
        L = 1500
        print("Non persistent", "Nodes: ", N, "Avg Packet: ", A)	# Display current values
        csma_cd(N, A, R, L, D, S, False)		# Call CSMA-CD Protocol method with persistence being false