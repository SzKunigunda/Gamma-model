# -*- coding: iso-8859-1 -*-
from __future__ import division
"""
Conversion of the Brunel network implemented in nest-1.0.13/examples/brunel.sli
to use PyNN.

Brunel N (2000) Dynamics of sparsely connected networks of excitatory and inhibitory spiking neurons.
J Comput Neurosci 8:183-208

Andrew Davison, UNIC, CNRS
May 2006

$Id: brunel.py 705 2010-02-03 16:06:52Z apdavison $

"""

from pyNN.utility import get_script_args, Timer
import numpy as numpi
import matplotlib.pyplot as plt
from detect_oscillations_15_50 import replay, ripple, gamma
from pyNN.random import NumpyRNG, RandomDistribution

simulator_name = "neuron"
exec("from pyNN.%s import *" % simulator_name)

# seed for random generator(s) used during simulation
kernelseed  = 43210987      

timer = Timer()

run_name = "ca3net8_gamma62_lif"

dt      = 0.1    # the resolution in ms
simtime = 10000.0 # Simulation time in ms (ideally 10s)
maxdelay   = 4.0    # synaptic delay in ms

epsilon_Pyr = 0.1  # connection probability
epsilon_Bas = 0.25
epsilon_Sli = 0.1

N_Pyr_all = 3600  # number of cells
N_Bas = 200
N_Sli = 200
N_neurons = N_Pyr_all + N_Bas + N_Sli

NP = 10   # number of excitatory subpopulations
N_Pyr = int(N_Pyr_all / NP) # number of pyramidal cells in each subpopulation

C_Exc  = int(epsilon_Pyr*N_Pyr_all) # number of excitatory synapses per neuron
C_Inh  = int(epsilon_Bas*N_Bas) # number of fast inhibitory synapses per neuron
C_SlowInh = int(epsilon_Sli*N_Sli) # number of slow inhibitory synapses per neuron
#C_tot = C_Inh+C_Exc      # total number of synapses per neuron

# number of synapses---just so we know
N_syn = (C_Exc+1)*N_neurons + C_Inh*(N_Pyr_all+N_Bas) + C_SlowInh*N_Pyr_all

# Initialize the parameters of the integrate and fire neurons

gL_Pyr = 2.5 # 3.3333 in SPW
tauMem_Pyr = 80.0 # 60.0 in SPW
Cm_Pyr = tauMem_Pyr * gL_Pyr
Vrest_Pyr = -60.0 # -70.0 in SPW
reset_Pyr = -60.0
theta_Pyr = -50.0
tref_Pyr = 5.0

gL_Bas = 7.1429
tauMem_Bas = 14.0
Cm_Bas = tauMem_Bas * gL_Bas
Vrest_Bas = -60.0 # -70.0 in SPW
reset_Bas = -55.0
theta_Bas  = -45.0
tref_Bas = 2.0

gL_Sli = 4.0
tauMem_Sli = 40.0
Cm_Sli = tauMem_Sli * gL_Sli
Vrest_Sli = -70.0
reset_Sli = -55.0
theta_Sli  = -45.0
tref_Sli = 2.0

# Initialize the synaptic parameters
J_PyrExc  = 0.02 # 0.15 in SPW  # in case of no recurrent connection, this parameter would be 0
J_PyrInh  = 2.0 # 4.0 in SPW
J_BasExc  = 0.3 # 1.5 in SPW
J_BasInh  = 2.0 # 4.0 in SPW
J_PyrSlowInh = 1.2 # 3.0 in SPW
J_SliExc = 0.02 # 0.1 in SPW
J_PyrExt = 0.3
J_PyrMF = 5.0
J_BasExt = 0.3
J_SliExt = 0.3

# Potentiated synapses
dpot = 10.0       # degree of potentiation
J_PyrPot = (1 + dpot) * J_PyrExc

# Synaptic reversal potentials
E_Exc = 0.0
E_Inh = -70.0

# Synaptic time constants
tauSyn_PyrExc = 10.0
tauSyn_PyrInh = 3.0
tauSyn_BasExc = 3.0
tauSyn_BasInh = 1.5
tauSyn_SliExc = 5.0
tauSyn_PyrSlowInh = 30.0

# Synaptic delays
delay_PyrExc = 3.0
delay_PyrInh = 1.5
delay_BasExc = 3.0
delay_BasInh = 1.5
delay_SliExc = 3.0
delay_PyrSlowInh = 2.0

p_rate_pyr = 1.0e-8 # input stenght
p_rate_bas = 1.0e-8
p_rate_sli = 1.0e-8

cell_params_Pyr= {"cm":        Cm_Pyr,
                    "tau_m":        tauMem_Pyr,
                    "v_rest":        Vrest_Pyr,
                    "e_rev_E":       E_Exc,
                    "e_rev_I":       E_Inh,
                    "tau_syn_E": tauSyn_PyrExc,
                    "tau_syn_I": tauSyn_PyrInh,
                    "tau_refrac":      tref_Pyr,
                    "v_reset":    reset_Pyr,
                    "v_thresh":       theta_Pyr}

cell_params_Bas= {"cm":        Cm_Bas,
                    "tau_m":        tauMem_Bas,
                    "v_rest":        Vrest_Bas,
                    "e_rev_E":       E_Exc,
                    "e_rev_I":       E_Inh,
                    "tau_syn_E": tauSyn_BasExc,
                    "tau_syn_I": tauSyn_BasInh,
                    "tau_refrac":      tref_Bas,
                    "v_reset":    reset_Bas,
                    "v_thresh":       theta_Bas}

cell_params_Sli= {"cm":        Cm_Sli,
                    "tau_m":        tauMem_Sli,
                    "v_rest":        Vrest_Sli,
                    "e_rev_E":       E_Exc,
                    "e_rev_I":       E_Inh,
                    "tau_syn_E": tauSyn_SliExc,
                    "tau_syn_I": tauSyn_BasInh,
                    "tau_refrac":      tref_Sli,
                    "v_reset":    reset_Sli,
                    "v_thresh":       theta_Sli}
 


# Creating a range of excitatory inputs

first = 10.0 
last = 35.0 
dataPoints = 20
excitations_mf = numpi.linspace(first, last, dataPoints)
X = numpi.zeros((19,dataPoints))


# === Build the network ======================================================== 
for k in range (0, dataPoints):
	# clear all existing network elements and set resolution and limits on delays.
	# For NEST, limits must be set BEFORE connecting any elements

	#extra = {'threads' : 2}
	extra = {}
	
	p_rate_mf = excitations_mf[k]
	print 'p_rate_mf=', p_rate_mf
	
	rank = setup(timestep=dt, max_delay=maxdelay, **extra)
	np = num_processes()
	import socket
	host_name = socket.gethostname()
	print "Host #%d is on %s" % (rank+1, host_name)

	if extra.has_key('threads'):
		print "%d Initialising the simulator with %d threads..." %(rank, extra['threads'])
	else:
		print "%d Initialising the simulator with single thread..." %(rank)

	# Small function to display information only on node 1
	def nprint(s):
		if (rank == 0):
			print s

	timer.start() # start timer on construction    

	print "%d Setting up random number generator" %rank
	rng = NumpyRNG(kernelseed, parallel_safe=True)

        # Initialising membrane potential to random values
	vrest_sd = 5
	vrest_distr = RandomDistribution('uniform', [Vrest_Pyr - numpy.sqrt(3)*vrest_sd, Vrest_Pyr + numpy.sqrt(3)*vrest_sd], rng)

	Pyr_net = []

	for sp in range(NP):
		print "%d Creating pyramidal cell population %d  with %d neurons." % (rank, sp, N_Pyr)
		Pyr_subnet = Population((N_Pyr,),IF_cond_exp,cell_params_Pyr)
		for cell in Pyr_subnet:
			vrest_rval = vrest_distr.next(1)
			cell.set_parameters(v_rest=vrest_rval)
		Pyr_net.append(Pyr_subnet)

	print "%d Creating basket cell population with %d neurons." % (rank, N_Bas)
	Bas_net = Population((N_Bas,),IF_cond_exp,cell_params_Bas)

	print "%d Creating slow inhibitory population with %d neurons." % (rank, N_Sli)
	Sli_net = Population((N_Sli,),IF_cond_exp,cell_params_Sli)

	# Creating external input - is this correct on multiple threads?
	Pyr_input = []

	for sp in range(NP):
		print "%d Creating pyramidal cell external input %d with rate %g spikes/s." % (rank, sp, p_rate_pyr)
		pyr_poisson = Population((N_Pyr,), SpikeSourcePoisson, {'rate': p_rate_pyr})
		Pyr_input.append(pyr_poisson)

	Pyr_input_MF = []

	for sp in range(NP):
		print "%d Creating pyramidal cell external input %d with rate %g spikes/s." % (rank, sp, p_rate_mf)
		pyr_poisson = Population((N_Pyr,), SpikeSourcePoisson, {'rate': p_rate_mf})
		Pyr_input_MF.append(pyr_poisson)

	print "%d Creating basket cell external input with rate %g spikes/s." % (rank, p_rate_bas)
	bas_poisson = Population((N_Bas,), SpikeSourcePoisson, {'rate': p_rate_bas})

	print "%d Creating slow inhibitory cell external input with rate %g spikes/s." % (rank, p_rate_sli)
	sli_poisson = Population((N_Sli,), SpikeSourcePoisson, {'rate': p_rate_sli})

	# Record spikes
	for sp in range(NP):
		print "%d Setting up recording in excitatory population %d." % (rank, sp)
		Pyr_net[sp].record()
		Pyr_net[sp][[0, 1]].record_v()

	print "%d Setting up recording in basket cell population." % rank
	Bas_net.record()
	Bas_net[[0, 1]].record_v()

	print "%d Setting up recording in slow inhibitory population." % rank
	Sli_net.record()
	Sli_net[[0, 1]].record_v()

	PyrExc_Connector = FixedProbabilityConnector(epsilon_Pyr, weights=J_PyrExc, delays=delay_PyrExc)
	PyrPot_Connector = FixedProbabilityConnector(epsilon_Pyr, weights=J_PyrPot, delays=delay_PyrExc)
	PyrInh_Connector = FixedProbabilityConnector(epsilon_Bas, weights=J_PyrInh, delays=delay_PyrInh)
	BasExc_Connector = FixedProbabilityConnector(epsilon_Pyr, weights=J_BasExc, delays=delay_BasExc)
	BasInh_Connector = FixedProbabilityConnector(epsilon_Bas, weights=J_BasInh, delays=delay_BasInh)
	SliExc_Connector = FixedProbabilityConnector(epsilon_Pyr, weights=J_SliExc, delays=delay_SliExc)
	PyrSlowInh_Connector = FixedProbabilityConnector(epsilon_Sli, weights=J_PyrSlowInh, delays=delay_PyrSlowInh)
	PyrExt_Connector = OneToOneConnector(weights=J_PyrExt, delays=dt)
	PyrMF_Connector = OneToOneConnector(weights=J_PyrMF, delays=dt)
	BasExt_Connector = OneToOneConnector(weights=J_BasExt, delays=dt)
	SliExt_Connector = OneToOneConnector(weights=J_SliExt, delays=dt)

	Pyr_to_Pyr = []
	Bas_to_Pyr = []
	Sli_to_Pyr = []
	Ext_to_Pyr = []
	MF_to_Pyr = []

	for post in range(NP):
		P2P_post = []
		Pyr_to_Pyr.append(P2P_post)
		for pre in range(NP):
			print "%d Connecting pyramidal cell subpopulations %d and %d." % (rank, pre, post)
			if pre == post:
				P2P_sub = Projection(Pyr_net[pre], Pyr_net[post], PyrPot_Connector, rng=rng, target="excitatory")
			else:
				P2P_sub = Projection(Pyr_net[pre], Pyr_net[post], PyrExc_Connector, rng=rng, target="excitatory")
			print "Pyr --> Pyr\t\t", len(P2P_sub), "connections"
			Pyr_to_Pyr[post].append(P2P_sub)
			B2P_sub = Projection(Bas_net, Pyr_net[post], PyrInh_Connector, rng=rng, target="inhibitory")
		print "Bas --> Pyr\t\t", len(B2P_sub), "connections"
		Bas_to_Pyr.append(B2P_sub)
		S2P_sub = Projection(Sli_net, Pyr_net[post], PyrSlowInh_Connector, rng=rng, target="inhibitory")
		print "SlowInh --> Pyr\t\t", len(S2P_sub), "connections"
		Sli_to_Pyr.append(S2P_sub)
		E2P_sub = Projection(Pyr_input[post], Pyr_net[post], PyrExt_Connector, target="excitatory")
		print "Ext --> Pyr\t", len(E2P_sub), "connections"
		Ext_to_Pyr.append(E2P_sub)
		MF2P_sub = Projection(Pyr_input_MF[post], Pyr_net[post], PyrMF_Connector, target="excitatory")
		print "MF --> Pyr\t", len(MF2P_sub), "connections"
		MF_to_Pyr.append(MF2P_sub)

	Pyr_to_Bas = []

	print "%d Connecting basket cell population." % (rank)
	for pre in range(NP):
		P2B_sub = Projection(Pyr_net[pre], Bas_net, BasExc_Connector, rng=rng, target="excitatory")
		print "Pyr --> Bas\t\t", len(P2B_sub), "connections"
		Pyr_to_Bas.append(P2B_sub)
	Bas_to_Bas = Projection(Bas_net, Bas_net, BasInh_Connector, rng=rng, target="inhibitory")
	print "Bas --> Bas\t\t", len(Bas_to_Bas), "connections"
	Ext_to_Bas = Projection(bas_poisson, Bas_net, BasExt_Connector, target="excitatory")
	print "Ext --> Bas\t", len(Ext_to_Bas), "connections"

	Pyr_to_Sli = []

	print "%d Connecting slow inhibitory population." % (rank)
	for pre in range(NP):
		P2S_sub = Projection(Pyr_net[pre], Sli_net, SliExc_Connector, rng=rng, target="excitatory")
		print "Pyr --> SlowInh\t\t", len(P2S_sub), "connections"
		Pyr_to_Sli.append(P2S_sub)
	Ext_to_Sli = Projection(sli_poisson, Sli_net, SliExt_Connector, target="excitatory")
	print "Ext --> SlowInh\t", len(Ext_to_Sli), "connections"

	# read out time used for building
	buildCPUTime = timer.elapsedTime()
	# === Run simulation ===========================================================

	# run, measure computer time
	timer.start() # start timer on construction
	print "%d Running simulation for %g ms." % (rank, simtime)
	run(simtime)
	simCPUTime = timer.elapsedTime()

	print "%d Writing data to file." % rank

	filename_spike_pyr = []
	filename_v_pyr = []
	for sp in range(NP):
		filename_spike_sub = "Results/%s_pyr%d_np%d_%s.ras" % (run_name, sp, np, simulator_name) # output file for excit. population
		filename_spike_pyr.append(filename_spike_sub)
		filename_v_sub = "Results/%s_pyr%d_np%d_%s.v" % (run_name, sp, np, simulator_name) # output file for membrane potential traces
		filename_v_pyr.append(filename_v_sub)
	filename_spike_bas  = "Results/%s_bas_np%d_%s.ras" % (run_name, np, simulator_name) # output file for basket cell population  
	filename_spike_sli  = "Results/%s_sli_np%d_%s.ras" % (run_name, np, simulator_name) # output file for slow inhibitory population
	filename_v_bas = "Results/%s_bas_np%d_%s.v"   % (run_name, np, simulator_name) # output file for membrane potential traces
	filename_v_sli = "Results/%s_sli_np%d_%s.v"   % (run_name, np, simulator_name) # output file for membrane potential traces

	# write data to file
	for sp in range(NP):
		Pyr_net[sp].printSpikes(filename_spike_pyr[sp])
		Pyr_net[sp].print_v(filename_v_pyr[sp])
	Bas_net.printSpikes(filename_spike_bas)
	Bas_net.print_v(filename_v_bas)
	Sli_net.printSpikes(filename_spike_sli)
	Sli_net.print_v(filename_v_sli)

	Pyr_rate = 0
	for sp in range(NP):
		Pyr_rate_sub = Pyr_net[sp].meanSpikeCount()*1000.0/simtime
		Pyr_rate = Pyr_rate + Pyr_rate_sub / NP
	Bas_rate = Bas_net.meanSpikeCount()*1000.0/simtime
	Sli_rate = Sli_net.meanSpikeCount()*1000.0/simtime

	# get the average spike rate of piramidals

	Pyr_spike_time = []

	for sp in range(NP):
		Pyr_Spikes = Pyr_net[sp].getSpikes()
		Pyr_spike_time = numpi.append(Pyr_spike_time,Pyr_Spikes[:,1])

	b = numpi.linspace(0,1000,1001)
	hist_p, bin_edges_p = numpi.histogram(Pyr_spike_time,b)


	Pyr_avg_rate = (hist_p*1000)/N_Pyr_all


	# get the average spike rate of baskets

	Bas_spike_time=Bas_net.getSpikes()
	hist_b, bin_edges_b = numpi.histogram(Bas_spike_time[:,1],b)
	Bas_avg_rate = (hist_b*1000)/N_Bas


	
	# detect oscillations

	meanEr, rEAC, maxEAC, tMaxEAC, maxEACR, tMaxEACR, fE, PxxE, avgRippleFE, ripplePE = ripple(Pyr_avg_rate, 1000)
	avgGammaFE, gammaPE = gamma(fE, PxxE)
	
	meanIr, rIAC, maxIAC, tMaxIAC, maxIACR, tMaxIACR, fI, PxxI, avgRippleFI, ripplePI = ripple(Bas_avg_rate, 1000)
	avgGammaFI, gammaPI = gamma(fI, PxxI)
        

	# saving the results into a matrix

	X[:, k] = [p_rate_mf,
               meanEr, maxEAC, tMaxEAC, maxEACR, tMaxEACR,
               meanIr, maxIAC, tMaxIAC, maxIACR, tMaxIACR,
               avgRippleFE, ripplePE, avgGammaFE, gammaPE,
               avgRippleFI, ripplePI, avgGammaFI, gammaPI]
	

	# write a short report

	nprint("\n--- CA3 Network Simulation %d ---" % k) 
	nprint("Nodes              : %d" % np)
	nprint("Number of Neurons  : %d" % N_neurons)
	nprint("Number of Synapses : %d" % N_syn)
	nprint("Small-amplitude Pyr input firing rate  : %g" % p_rate_pyr)
	nprint("Large-amplitude Pyr input firing rate  : %g" % p_rate_mf)
	nprint("Bas input firing rate  : %g" % p_rate_bas)
	nprint("SlowInh input firing rate  : %g" % p_rate_sli)
	nprint("Pyr -> Pyr weight  : %g" % J_PyrExc)
	nprint("Pyr -> Pyr potentiated weight  : %g" % J_PyrPot)
	nprint("Pyr -> Bas weight  : %g" % J_BasExc)
	nprint("Bas -> Pyr weight  : %g" % J_PyrInh)
	nprint("Bas -> Bas weight  : %g" % J_BasInh)
	nprint("Pyr -> SlowInh weight  : %g" % J_SliExc)
	nprint("SlowInh -> Pyr weight  : %g" % J_PyrSlowInh)
	nprint("Pyramidal cell rate    : %g Hz" % Pyr_rate)
	nprint("Basket cell rate    : %g Hz" % Bas_rate)
	nprint("Slow inhibitory rate    : %g Hz" % Sli_rate)
	nprint("Build time         : %g s" % buildCPUTime)   
	nprint("Simulation time    : %g s" % simCPUTime)

	# PLOT

	# Pyr population
        logic1 = isinstance(PxxE, float) # checks weather it is nan value
        print logic1
        logic2 = isinstance(PxxI, float)
        print logic2
        if not(logic1):
		fig1 = plt.figure(figsize=(14, 20))

		ax = fig1.add_subplot(4, 1, 1)
		ax.plot(numpi.linspace(0, 1000, len(Pyr_avg_rate)), Pyr_avg_rate, 'b-')
		ax.set_title('Pyramidal population rate | Mf exitation = %.2f Hz' % p_rate_mf)
		ax.set_xlabel('Time [ms]')
		ax.set_ylabel('Pyr. rate [Hz]')

		PxxEPlot = 10 * numpi.log10(PxxE / max(PxxE))

		fE = numpi.asarray(fE)
		rippleS = numpi.where(145 < fE)[0][0]
		rippleE = numpi.where(fE < 250)[0][-1]
		gammaS = numpi.where(15 < fE)[0][0]
		gammaE = numpi.where(fE < 50)[0][-1]
		fE.tolist()

		PxxRipple = PxxE[rippleS:rippleE]
		PxxGamma = PxxE[gammaS:gammaE]

		fRipple = fE[rippleS:rippleE]
		fGamma = fE[gammaS:gammaE]

		PxxRipplePlot = 10 * numpi.log10(PxxRipple / max(PxxE))
		PxxGammaPlot = 10 * numpi.log10(PxxGamma / max(PxxE))

		ax1 = fig1.add_subplot(4, 1, 2)
		ax1.plot(fE, PxxEPlot, 'b-', marker='o', linewidth=1.5)
		ax1.plot(fRipple, PxxRipplePlot, 'r-', marker='o', linewidth=2)
		ax1.plot(fGamma, PxxGammaPlot, 'k-', marker='o', linewidth=2)
		ax1.set_title('Power Spectrum Density')
		ax1.set_xlim([0, 500])
		ax1.set_xlabel('Frequency [Hz]')
		ax1.set_ylabel('PSD [dB]')
		
		ax6 = fig1.add_subplot(4, 1, 3)
		ax6.plot(numpi.linspace(0, 1000, len(Bas_avg_rate)), Bas_avg_rate, 'b-')
		ax6.set_title('Bas. population rate | Mf exitation = %.2f Hz' % p_rate_mf)
		ax6.set_xlabel('Time [ms]')
		ax6.set_ylabel('Bas. rate [Hz]')
        
        if not(logic2):
		PxxIPlot = 10 * numpi.log10(PxxI / max(PxxI))

		fI = numpi.asarray(fI)
		rippleS = numpi.where(145 < fI)[0][0]
		rippleE = numpi.where(fI < 250)[0][-1]
		gammaS = numpi.where(15 < fI)[0][0]
		gammaE = numpi.where(fI < 50)[0][-1]
		fI.tolist()

		PxxRipple = PxxI[rippleS:rippleE]
		PxxGamma = PxxI[gammaS:gammaE]

		fRipple = fI[rippleS:rippleE]
		fGamma = fI[gammaS:gammaE]

		PxxRipplePlot = 10 * numpi.log10(PxxRipple / max(PxxI))
		PxxGammaPlot = 10 * numpi.log10(PxxGamma / max(PxxI))

		ax7 = fig1.add_subplot(4, 1, 4)
		ax7.plot(fI, PxxIPlot, 'b-', marker='o', linewidth=1.5)
		ax7.plot(fRipple, PxxRipplePlot, 'r-', marker='o', linewidth=2)
		ax7.plot(fGamma, PxxGammaPlot, 'k-', marker='o', linewidth=2)
		ax7.set_title('Power Spectrum Density')
		ax7.set_xlim([0, 500])
		ax7.set_xlabel('Frequency [Hz]')
		ax7.set_ylabel('PSD [dB]')

	fig1.tight_layout()
	fig1.savefig('gammaPSD_mfexitation%.2fhz.png' %p_rate_mf)

fig2 = plt.figure(figsize=(10, 8))

ax2 = fig2.add_subplot(2, 1, 1)
ax2.plot(excitations_mf, X[13, :], label='Gamma freq (exc.)', color='blue', linewidth=2, marker='o')
ax3 = ax2.twinx()
ax3.plot(excitations_mf, X[14, :], label='Gamma power (exc.)', color='red', linewidth=2, marker='|')
ax2.set_xlim(first, last)
ax2.set_ylabel(ylabel='freq [Hz]', color='blue')
ax2.set_ylim([numpi.nanmin(X[13, :])-5, numpi.nanmax(X[13, :])+8])
ax3.set_ylabel(ylabel='power %', color='red')
ax3.set_ylim([0, 100])
ax2.set_title('Gamma oscillation')
ax2.legend(loc=2)
ax3.legend()

ax4 = fig2.add_subplot(2, 1, 2)
ax4.plot(excitations_mf, X[17, :], label='Gamma freq (inh.)', color='green', linewidth=2, marker='o')
ax5 = ax4.twinx()
ax5.plot(excitations_mf, X[18, :], label='Gamma power (inh.)', color='red', linewidth=2, marker='|')
ax4.set_xlim(first, last)
ax4.set_ylabel(ylabel='freq [Hz]', color='green')
ax4.set_ylim([numpi.nanmin(X[17, :])-5, numpi.nanmax(X[17, :])+8])
ax5.set_ylabel(ylabel='power %', color='red')
ax5.set_ylim([0, 100])
ax4.set_xlabel('Mf excitation [Hz]')
ax4.legend(loc=2)
ax5.legend()

fig2.tight_layout()
fig2.savefig('gammapower_exitation_range%.2fhz-%.2fhz.png' %(first,last))

# plt.show()


plt.close('all')

  
# === Clean up and quit ========================================================

end()
