import multiprocessing

def cpu_exhaustion():
	while True:
		pass # Creates an infinite loop to keep CPU busy
if __name__ == "__main__":
	print("Running CPU Attack...")
	num_cores = multiprocessing.cpu_count() # Returns the number of cores
	processes = []

	for i in range(num_cores): # Creates a process for each core, in which runs an infinite loop
		p = multiprocessing.Process(target=cpu_exhaustion)
		p.start() # Start the infinite loop
		processes.append(p) # Saves the processes

	for i in processes: # Waits for each process to finish, which will never happen
		p.join()
