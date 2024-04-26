## Mock HPC lab - Data Grid (tech 2)

The second tech lab drills into parallel data extraction using 
techniques and technologies commonly associated with High Performance 
Computing (HPC). Our projct is scaled back in size/breath to a single 
computer nevertheless, it encompases strategies for large scale 
simulations. 

In our project we are going to write a simulation that simulates a 
24 hours (day), a week, a month, or a year in New York City's traffic 
enforcement division. 

This will be an interesting experiment. There is no pre-coded structure 
to leverage from. This becomes your responsibility to research and code. 
A significatant amount of time and effort will be required for this mini. 


### Technologies

Our mock HPC is primarily C/C++ with some frontend initiation in Python. 
The key tools (technical components) are focusing on parallel coding 
techniques using:

   * Threading (OpenMP)
   * Multi-process communication using MPI library (e.g., OpenMPI)
   * Shared memory
   * Choice: mpi4py or py4mpi


### Seed code

Example/Seed code and data for parsing the NYC data is provided in 
Java. However, as the above introduction eluded to, this mini is 
C/C++ and some Python. The Java code should not be part of a team's
solution.


### Tasks

You will need to think many concepts. Here are some (not all) of the
concepts you will need to work on:

   * Sinks and Sources with the simulation. Sinks are 
     consumers of data, and sources are generators.
   * Simulation time vs real-time. Rate of simulation 
     obviously must be faster than wall clock time as 
     we would never have our code complete
   * Scalability, using the MPI job scheduling/scaling to
     increase/decrease the number of processes. Is there a
     maximum or minimum number of processes?
