"""
Author: Michael Moss
Contact: mikejmoss3@gmail.com
Last Edited: 2020-08-17


This code defines a number of Lorentz distribution shapes distribution shapes to be used in the simulation of a GRB prompt jet 
made of n consecutive shells 

"""

import numpy as np
import matplotlib.pyplot as plt 
import cosmologicalconstants as cc
from utils import *

def step(dte, g1=100, g2=400, numshells=5000, mfrac=0.5,E_dot=1e52):
	"""
	Distribute the Lorentz factors of the shells into a step function. 
	Params: 
	dte = time between shell launches, this can be specific by a single float to apply a constant time step through out the jet evolution or can be a array of the shell emission times
	g1 = Lorentz factor of the group of shells launched earlier
	g2 = Lorentz factor of the group of shells launched later
	numshells = the total number of shells launched
	mfrac = the mass fraction of the group of shells launched earlier, e.g., mfrac = M_1 / M_total

	"""

	# Number of shells with Lorentz factor g1: 
	n1 =  int(numshells / ( ((1-mfrac)*g2/(mfrac*g1)) + 1 ))
	# Number of shells with Lorentz factor g2: 
	n2 = int(numshells - n1)

	# Make array of shells
	# This array stores the radius, lorentz factor, mass, and emission time of each shell. The last column is used to record what the status of the shell is.
	# Status indicator: 0 = deactived, 1 = active and launched, 2 = not launched
	shell_arr = np.ndarray(shape=numshells,dtype=[('RADIUS',float),('GAMMA',float),('MASS',float),('TE',float),('STATUS',float)])

	# Set the Lorentz factors for each section of the step distribution
	shell_arr[0:n1]['GAMMA'] = np.ones(shape=n1)*g1
	shell_arr[n1::]['GAMMA'] = np.ones(shape=n2)*g2

	# Set the Mass for each shell 
	shell_arr['MASS'] = E_dot*dte/shell_arr['GAMMA']/cc.c**2


	# Check if a single time step was given or a list of launch times
	# If a list of launch times was given was given
	if hasattr(dte,"__len__"):
		# Check if the list is the same size as the number of shells
		if len(dte) != numshells:
			print("The list of shell launch times must be the same size as the number of shells.")
		shell_arr['TE'] = -dte
	# Else if a single constant difference between launch time
	else:
		for i in range(numshells):
			shell_arr[i]['TE'] = -i*dte

	# Calculate the shell position based on when the shell will be launched
	shell_arr['RADIUS'] = [cc.c*beta(shell_arr['GAMMA'][i])*shell_arr['TE'][i]for i in range(len(shell_arr))]
	shell_arr['RADIUS'][0] +=1 # Eliminates divide by zero error and is insignificantly small.

	# Deactivate all shells except the initial one
	shell_arr['STATUS'] = np.ones(shape=numshells,dtype=int)

	return shell_arr

def oscillatory(dte,gmin=100,gmax=400,numshells=5000,median=333,ampf=2/3,freq=5,decay=0.5,E_dot=1e52):
	"""
	Distribution shells with an oscillatory Lorentz distribution 
	Params:
	dte = time between shell launches, this can be specific by a single float to apply a constant time step through out the jet evolution or can be a array of the shell emission times
	g1 = Lorentz factor of the group of shells launched earlier
	g2 = Lorentz factor of the group of shells launched later
	numshells = the total number of shells launched
	freq = frequency of the oscillations in the distribution
	decay = used to modulate the decay rate, number multiplied by the halfl ife time scale
	"""

	# Make array of shells
	# This array stores the radius, lorentz factor, mass, and emission time of each shell. The last column is used to record what the status of the shell is.
	shell_arr = np.ndarray(shape=numshells,dtype=[('RADIUS',float),('GAMMA',float),('MASS',float),('TE',float),('STATUS',float)])

	# Check if a single time step was given or a list of launch times
	# If a list of launch times was given was given
	if hasattr(dte,"__len__"):
		# Check if the list is the same size as the number of shells
		if len(dte) != numshells:
			print("The list of shell launch times must be the same size as the number of shells.")
		shell_arr['TE'] = -dte
	# Else if a single constant difference between launch time
	else:
		for i in range(numshells):
			shell_arr[i]['TE'] = -i*dte

	# Set the Lorentz factors for each section of the step distribution
	shell_inds = np.linspace(0,numshells,num=numshells)
	shell_arr['GAMMA'] = median * ( 1 + ampf*np.cos( freq*np.pi*(1 - shell_inds/numshells) ) )*np.exp(- decay*shell_inds/numshells)

	# Set the Mass for each shell 
	shell_arr['MASS'] = E_dot*dte/shell_arr['GAMMA']/cc.c**2
	


	# Calculate the shell position based on when the shell will be launched
	shell_arr['RADIUS'] = [cc.c*beta(shell_arr['GAMMA'][i])*shell_arr['TE'][i]for i in range(len(shell_arr))]
	shell_arr['RADIUS'][0] +=1 # Eliminates divide by zero error and is insignificantly small.

	# Deactivate all shells except the initial one
	shell_arr['STATUS'] = np.ones(shape=numshells,dtype=int)

	return shell_arr


def plot_lorentz_dist(ax, shell_arr,label=None,xlabel=True,ylabel=True,fontsize=14,fontweight='bold',linestyle='solid'):
	"""
	Method to plot the given Lorentz factor distribution

	Attributes:
	ax = the matplotlib.pyplot.axes instance to make the plot on
	shell_arr = the array contained the shell distribution to be plotted
	label = optional label for the plot
	"""

	# To match paper graphics
	flipped_mass_arr = np.flip(shell_arr['MASS'])
	flipped_gamma_arr = np.flip(shell_arr['GAMMA'])

	# Cumulative mass
	masscum = np.cumsum(flipped_mass_arr)
	massfraccum = masscum/masscum[-1]

	# Plot distribution
	line, = ax.step(massfraccum,flipped_gamma_arr,where='pre',linestyle=linestyle)

	if label is not None:
		line.set_label(label)
	if xlabel is True:
		ax.set_xlabel(r'M/M$_{tot}$',fontsize=fontsize,fontweight=fontweight)
	if ylabel is True:
		ax.set_ylabel(r'$\Gamma$',fontsize=fontsize,fontweight=fontweight)

	for tick in ax.xaxis.get_major_ticks():
	    tick.label1.set_fontsize(fontsize=fontsize)
	    tick.label1.set_fontweight(fontweight)
	for tick in ax.yaxis.get_major_ticks():
	    tick.label1.set_fontsize(fontsize=fontsize)
	    tick.label1.set_fontweight(fontweight)


