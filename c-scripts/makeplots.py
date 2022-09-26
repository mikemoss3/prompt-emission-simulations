"""
Author: Michael Moss
Contact: mikejmoss3@gmail.com
Last Edited: 2021-11-26


Meta script to plot desired simulation results created by c++ code.

"""
import matplotlib.pyplot as plt
import numpy as np
import subprocess
# import cosmologicalconstants as cc
import scipy.integrate as integrate 
from matplotlib.widgets import TextBox
from matplotlib.lines import Line2D
from matplotlib.animation import FuncAnimation, PillowWriter 
from matplotlib.ticker import FormatStrFormatter

from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset

kb_kev = 8.617*1e-8
kev_to_erg = 1.6022*np.power(10.,-9.)
planck_kev = 4.136 * np.power(10,-18.) # keV Hz^-1

def plot_aesthetics(ax,fontsize=14,fontweight='bold'):
	"""
	This function is used to make bold and increase the font size of all plot tick markers
	"""

	for tick in ax.xaxis.get_major_ticks():
		tick.label1.set_fontsize(fontsize=fontsize)
		tick.label1.set_fontweight(fontweight)

		tick.label2.set_fontsize(fontsize=fontsize)
		tick.label2.set_fontweight(fontweight)

	for tick in ax.yaxis.get_major_ticks():
		tick.label1.set_fontsize(fontsize=fontsize)
		tick.label1.set_fontweight(fontweight)

		tick.label2.set_fontsize(fontsize=fontsize)
		tick.label2.set_fontweight(fontweight)
		
##############################################################################################################################

def plot_lor_dist(file_name,ax=None,fig=None,save_pref=None,xlabel=True,ylabel=True,label=None,fontsize=14,fontweight='bold',marker='.', linestyle="solid",show_zoomed = False, separator_string = "// Next step\n",title=True):
	"""
	Method to plot the given Lorentz factor distribution saved in the text file with path name "file_name".
	Multiple snapshots of the Lorentz distribution can be given in a single file. Each Lorentz distribution must be separated by a line with the string indicated by "separator_string".
	If more than one snapshot is provided, the snapshots can be scrolled through with the left and right arrow keys. 

	The Lorentz distribution file must contain the columns: 
	RADIUS - Radius of the shell
	GAMMA - Lorentz factor of the shell
	MASS - Mass of the shell
	TE - Time of emission of the shell
	STATUS - Status of the shell, this is used by the simulation code to indicate if a shell is still active or not. 

	Attributes:
	ax = the matplotlib.pyplot.axes instance to make the plot on
	save_pref = if not left as None, the plot will be saved and the file name will have this prefix
	xlabel, ylabel = indicate whether x- and y- labels should be included (boolean)
	label = optional label for the data set
	fontsize, fontweight = fontsize and fontweight of the plot font and labels on the plot
	linestyle = style of the plotting line 
	separator_string = the string between each snapshot of the Lorentz distribution
	"""

	# Load data
	lor_time_list, lor_dist_list = load_lor_dist(file_name)

	# Only select active shells. 
	for i in range(len(lor_dist_list)):
		lor_dist_list[i] = lor_dist_list[i][lor_dist_list[i]["STATUS"]==1]

	# Make plot instance if it doesn't exist
	if fig is None:
		fig = plt.figure()
	if ax is None:
		ax = fig.gca()
	ind = np.array([0])
	def on_press(event):
		if event.key == 'right':
			ind[0] +=1
		elif event.key == 'left':
			ind[0] -=1

		# Loop back to beginning 
		if(ind[0] == len(lor_time_list)):
			ind[0] = 0
		# Loop to the end
		if(ind[0] == -1):
			ind[0] = len(lor_time_list)-1

		# Update ejection time plot 
		# line_shell_ind.set_xdata(lor_dist_list[ind[0]]['TE'])
		# line_shell_ind.set_ydata(lor_dist_list[ind[0]]['GAMMA'])
		line_shell_ind.set_offsets(np.transpose([lor_dist_list[ind[0]]['TE'],lor_dist_list[ind[0]]['GAMMA']]))
		# ax[0].set_xlim(np.min(lor_dist_list[ind[0]]['TE']),np.max(lor_dist_list[ind[0]]['GAMMA']))

		# Update cumulative mass fraction plot 
		flipped_mass_arr = np.flip(lor_dist_list[ind[0]]['MASS'])
		flipped_gamma_arr = np.flip(lor_dist_list[ind[0]]['GAMMA'])
		# Cumulative mass
		masscum = np.cumsum(flipped_mass_arr)
		massfraccum = masscum/masscum[-1]
		line_mass_frac.set_xdata(massfraccum)
		line_mass_frac.set_ydata(flipped_gamma_arr)

		# Update radius plot 
		line_rad.set_offsets(np.transpose([lor_dist_list[ind[0]]['RADIUS'],lor_dist_list[ind[0]]['GAMMA']]))
		ax[1,0].set_xlim(np.min(lor_dist_list[ind[0]]['RADIUS']), np.max(lor_dist_list[ind[0]]['RADIUS']))

		# Update mass-radius plot 
		line_mass_rad.set_xdata(lor_dist_list[ind[0]]['RADIUS'])
		line_mass_rad.set_ydata(np.flip(massfraccum))
		ax[1,1].set_xlim(np.min(lor_dist_list[ind[0]]['RADIUS']), np.max(lor_dist_list[ind[0]]['RADIUS']))


		fig.suptitle("Emission Time = {0:.1e} sec".format(lor_time_list[ind[0]]),fontsize=fontsize,fontweight=fontweight)
		ax[1,0].ticklabel_format(axis='x',style='sci',scilimits=(0,2),useOffset=False)
		ax[1,1].ticklabel_format(axis='x',style='sci',scilimits=(0,2),useOffset=False)

		if (show_zoomed == True):

			line_mass_frac_zoom_x.set_xdata(massfraccum)
			line_mass_frac_zoom_x.set_ydata(flipped_gamma_arr)

			line_mass_frac_zoom_y.set_xdata(massfraccum)
			line_mass_frac_zoom_y.set_ydata(flipped_gamma_arr)

			line_rad_zoom_x.set_offsets(np.transpose([lor_dist_list[ind[0]]['RADIUS'],lor_dist_list[ind[0]]['GAMMA']]))

			line_rad_zoom_y.set_offsets(np.transpose([lor_dist_list[ind[0]]['RADIUS'],lor_dist_list[ind[0]]['GAMMA']]))
			ax_zoom_rad_y.set_xlim(lor_dist_list[ind[0]]['RADIUS'][int(len(lor_dist_list[ind[0]]['RADIUS'])/2)], np.max(lor_dist_list[ind[0]]['RADIUS']))

			ax_zoom_rad_x.ticklabel_format(axis='x',style='sci',scilimits=(0,2),useOffset=False)
			ax_zoom_rad_y.ticklabel_format(axis='x',style='sci',scilimits=(0,2),useOffset=False)

			ax_zoom_x.redraw_in_frame()
			ax_zoom_y.redraw_in_frame()
			ax_zoom_rad_x.redraw_in_frame()
			ax_zoom_rad_y.redraw_in_frame()



		# Redraw the figure to implement updates
		ax[0,0].redraw_in_frame()
		ax[0,1].redraw_in_frame()
		ax[1,0].redraw_in_frame()
		ax[1,1].redraw_in_frame()
		fig.canvas.draw_idle()

	fig.canvas.mpl_connect('key_press_event', on_press)

	## Plot distribution as a function of the shell number 
	line_shell_ind = ax[0,0].scatter(lor_dist_list[0]['TE'],lor_dist_list[0]['GAMMA'],marker=marker)
	ax[0,0].set_ylim(0)
	ax[0,0].invert_xaxis()

	## Plot the Lorentz distribution as a function of the mass fraction
	flipped_mass_arr = np.flip(lor_dist_list[0]['MASS'])
	flipped_gamma_arr = np.flip(lor_dist_list[0]['GAMMA'])

	# Cumulative mass
	masscum = np.cumsum(flipped_mass_arr)
	massfraccum = masscum/masscum[-1]

	# Plot distribution as a function of the mass fraction
	line_mass_frac, = ax[0,1].step(massfraccum,flipped_gamma_arr,where='pre',linestyle=linestyle,label=label)
	ax[0,1].set_ylim(0)

	## Plot Lorentz factor vs Radius
	line_rad = ax[1,0].scatter(lor_dist_list[0]['RADIUS'],lor_dist_list[0]['GAMMA'],marker=marker)
	ax[1,0].set_ylim(0)

	ax[1,0].ticklabel_format(axis='x',style='sci',scilimits=(0,2),useOffset=False)
	

	## Mass vs Radius
	line_mass_rad, = ax[1,1].step(lor_dist_list[0]['RADIUS'],np.flip(massfraccum),where='pre',linestyle=linestyle)

	ax[1,1].ticklabel_format(axis='x',style='sci',scilimits=(0,2),useOffset=False)

	if xlabel is True:
		ax[0,0].set_xlabel('Launch Time After Jet Start (sec)',fontsize=fontsize,fontweight=fontweight)
		ax[0,1].set_xlabel(r'M/M$_{tot}$',fontsize=fontsize,fontweight=fontweight)
		ax[1,0].set_xlabel(r'Radius (light second)',fontsize=fontsize,fontweight=fontweight)
		ax[1,1].set_xlabel(r'Radius (light second)',fontsize=fontsize,fontweight=fontweight)
	if ylabel is True:
		ax[0,0].set_ylabel(r'$\Gamma$',fontsize=fontsize,fontweight=fontweight)
		ax[0,1].set_ylabel(r'$\Gamma$',fontsize=fontsize,fontweight=fontweight)
		ax[1,0].set_ylabel(r'$\Gamma$',fontsize=fontsize,fontweight=fontweight)
		ax[1,1].set_ylabel('Mass (g)',fontsize=fontsize,fontweight=fontweight)


	if title == True:
		fig.suptitle("Emission Time = {0:.1e} sec".format(lor_time_list[0]),fontsize=fontsize,fontweight=fontweight)

	plot_aesthetics(ax[0,0],fontsize=fontsize,fontweight=fontweight)
	plot_aesthetics(ax[0,1],fontsize=fontsize,fontweight=fontweight)
	plot_aesthetics(ax[1,0],fontsize=fontsize,fontweight=fontweight)
	plot_aesthetics(ax[1,1],fontsize=fontsize,fontweight=fontweight)

	
	if (show_zoomed == True):
		# Zoom in on the lower Lorentz factor
		ax_zoom_x = ax[0,1].twinx()
		line_mass_frac_zoom_x, = ax_zoom_x.step(massfraccum,flipped_gamma_arr,where='pre',linestyle=linestyle,color="C1",alpha=0.5)
		ax_zoom_x.set_ylim(0,40)

		# Zoom in on the highest mass fraction 
		ax_zoom_y = ax[0,1].twiny()
		line_mass_frac_zoom_y, = ax_zoom_y.step(massfraccum,flipped_gamma_arr,where='pre',linestyle=linestyle,color="C2",alpha=0.5)
		ax_zoom_y.set_xlim(0.95,1.01)

		# Zoom in on the shells with lower Lorentz factors 
		ax_zoom_rad_x = ax[1,0].twinx()
		line_rad_zoom_x = ax_zoom_rad_x.scatter(lor_dist_list[0]['RADIUS'],lor_dist_list[0]['GAMMA'],marker=marker,color="C1",alpha=0.3)
		ax_zoom_rad_x.set_ylim(0,20)
		# Zoom in on the farthest shells 
		ax_zoom_rad_y = ax[1,0].twiny()
		line_rad_zoom_y = ax_zoom_rad_y.scatter(lor_dist_list[0]['RADIUS'],lor_dist_list[0]['GAMMA'],marker=marker,color="C2",alpha=0.3)
		ax_zoom_rad_y.set_xlim(lor_dist_list[0]['RADIUS'][int(len(lor_dist_list[0]['RADIUS'])/2)],np.max(lor_dist_list[0]['RADIUS']))

		ax_zoom_rad_x.ticklabel_format(axis='x',style='sci',scilimits=(0,2),useOffset=False)
		ax_zoom_rad_y.ticklabel_format(axis='x',style='sci',scilimits=(0,2),useOffset=False)

		plot_aesthetics(ax_zoom_x,fontsize=fontsize,fontweight=fontweight)
		plot_aesthetics(ax_zoom_y,fontsize=fontsize,fontweight=fontweight)
		plot_aesthetics(ax_zoom_rad_x,fontsize=fontsize,fontweight=fontweight)
		plot_aesthetics(ax_zoom_rad_y,fontsize=fontsize,fontweight=fontweight)
	

	if label is not None:
		ax[0,0].legend(fontsize=fontsize)

	plt.tight_layout()

	if save_pref is not None :
		plt.savefig('figs/{}-lorentz-dist.png'.format(save_pref))

##############################################################################################################################

def plot_lor_dist_simple(file_name,ax=None,fig=None,color="C0",save_pref=None,xlabel=True,ylabel=True,label=None,fontsize=14,fontweight='bold',marker='.', separator_string = "// Next step\n",joined=True,title=True,zoom_inset=False):
	"""
	Method to plot the given Lorentz factor distribution saved in the text file with path name "file_name".
	Multiple snapshots of the Lorentz distribution can be given in a single file. Each Lorentz distribution must be separated by a line with the string indicated by "separator_string".
	If more than one snapshot is provided, the snapshots can be scrolled through with the left and right arrow keys. 

	The Lorentz distribution file must contain the columns: 
	RADIUS - Radius of the shell
	GAMMA - Lorentz factor of the shell
	MASS - Mass of the shell
	TE - Time of emission of the shell
	STATUS - Status of the shell, this is used by the simulation code to indicate if a shell is still active or not. 

	Attributes:
	ax = the matplotlib.pyplot.axes instance to make the plot on
	save_pref = if not left as None, the plot will be saved and the file name will have this prefix
	xlabel, ylabel = indicate whether x- and y- labels should be included (boolean)
	label = optional label for the data set
	fontsize, fontweight = fontsize and fontweight of the plot font and labels on the plot
	linestyle = style of the plotting line 
	separator_string = the string between each snapshot of the Lorentz distribution
	"""

	# Load data
	lor_time_list, lor_dist_list = load_lor_dist(file_name)

	# Make plot instance if it doesn't exist
	if fig is None:
		fig = plt.figure()
	if ax is None:
		ax = fig.gca()

	ind = np.array([0])
	def on_press(event):
		if event.key == 'right':
			ind[0] +=1
		elif event.key == 'left':
			ind[0] -=1

		# Loop back to beginning 
		if(ind[0] == len(lor_time_list)):
			ind[0] = 0
		# Loop to the end
		if(ind[0] == -1):
			ind[0] = len(lor_time_list)-1

		# Update ejection time plot 
		if(joined == True):
			line_shell_ind.set_xdata(lor_dist_list[ind[0]]['TE'])
			line_shell_ind.set_ydata(lor_dist_list[ind[0]]['GAMMA'])
		if(joined == False):
			line_shell_ind.set_offsets(np.transpose([lor_dist_list[ind[0]]['TE'],lor_dist_list[ind[0]]['GAMMA']]))
		# ax[0].set_xlim(np.min(lor_dist_list[ind[0]]['TE']),np.max(lor_dist_list[ind[0]]['GAMMA']))

		if title == True:
			fig.suptitle("Emission Time = {0:.1e} sec".format(lor_time_list[ind[0]]),fontsize=fontsize,fontweight=fontweight)

		# Include zoom within an inset if specified 	
		if zoom_inset is True:
			if(joined == True):
				line_inset.set_xdata(lor_dist_list[ind[0]]['TE'])
				line_inset.set_ydata(lor_dist_list[ind[0]]['GAMMA'])
			elif(joined == False):
				line_inset.set_offsets(np.transpose([lor_dist_list[ind[0]]['TE'],lor_dist_list[ind[0]]['GAMMA']]))

		# Redraw the figure to implement updates
		ax.redraw_in_frame()
		fig.canvas.draw_idle()

	fig.canvas.mpl_connect('key_press_event', on_press)

	## Plot distribution as a function of the shell number 
	if(joined == True):
		line_shell_ind, = ax.step(lor_dist_list[0]['TE'],lor_dist_list[0]['GAMMA'],where="pre",color=color)
	elif(joined == False):
		line_shell_ind = ax.scatter(lor_dist_list[0]['TE'],lor_dist_list[0]['GAMMA'],marker=marker,color=color)

	# Include zoom within an inset if specified 	
	if zoom_inset is True:
		axins = ax.inset_axes([0.1, 0.5, 0.47, 0.47])
		if(joined == True):
			line_inset, = axins.step(lor_dist_list[0]['TE'],lor_dist_list[0]['GAMMA'],where="pre",color=color)
		elif(joined == False):
			line_inset = axins.scatter(lor_dist_list[0]['TE'],lor_dist_list[0]['GAMMA'],marker=marker,color=color)
		
		# sub region of the original image
		x1, x2, y1, y2 = 12, np.max(lor_dist_list[0]['TE']), 0.1, 20
		axins.set_xlim(x1, x2)
		axins.set_ylim(y1, y2)

		axins.invert_xaxis()

		plot_aesthetics(axins,fontsize=fontsize-2,fontweight=fontweight)


	ax.set_ylim(0,np.max(lor_dist_list[0]['GAMMA']+10))
	ax.set_xlim(0,np.max(lor_dist_list[0]['TE']))
	ax.invert_xaxis()

	if xlabel is True:
		ax.set_xlabel('Initial Ejection Time (sec)',fontsize=fontsize,fontweight=fontweight)
	if ylabel is True:
		ax.set_ylabel(r'$\Gamma$',fontsize=fontsize,fontweight=fontweight)


	if title == True:
		fig.suptitle("Emission Time = {0:.1e} sec".format(lor_time_list[0]),fontsize=fontsize,fontweight=fontweight)


	plot_aesthetics(ax,fontsize=fontsize,fontweight=fontweight)

	if label is not None:
		ax.legend(fontsize=fontsize)

	plt.tight_layout()

	if save_pref is not None :
		plt.savefig('figs/{}-lorentz-dist.png'.format(save_pref))


##############################################################################################################################

def plot_lor_dist_anim(file_name,ax=None,save_pref=None,xlabel=True,ylabel=True,label=None,fontsize=14,fontweight='bold',linestyle='solid', separator_string = "// Next step\n"):
	"""
	Method to make an animated gif of the Lorentz factor distribution saved in the text file with path name "file_name".
	Multiple snapshots of the Lorentz distribution can be given in a single file. Each Lorentz distribution must be separated by a line with the string indicated by "separator_string"

	The Lorentz distribution file must contain the columns: 
	RADIUS - Radius of the shell
	GAMMA - Lorentz factor of the shell
	MASS - Mass of the shell
	TE - Time of emission of the shell
	STATUS - Status of the shell, this is used by the simulation code to indicate if a shell is still active or not. 

	Attributes:
	ax = the matplotlib.pyplot.axes instance to make the plot on
	save_pref = if not left as None, the plot will be saved and the file name will have this prefix
	xlabel, ylabel = indicate whether x- and y- labels should be included (boolean)
	label = optional label for the data set
	fontsize, fontweight = fontsize and fontweight of the plot font and labels on the plot
	linestyle = style of the plotting line 
	separator_string = the string between each snapshot of the Lorentz distribution
	"""
	# Load data
	lor_time_list, lor_dist_list = load_lor_dist(file_name)

	# Make plot instance if it doesn't exist
	fig, ax = plt.subplots(1,2,figsize=(16, 6))	

	# Plot distribution as a function of the shell number 
	line_shell_ind, = ax[0].step(lor_dist_list[0]['TE'],lor_dist_list[0]['GAMMA'],where='pre',linestyle=linestyle,label=label)
	ax[0].set_ylim(0)
	ax[0].invert_xaxis()

	# Plot the Lorentz distribution as a function of the mass fraction
	flipped_mass_arr = np.flip(lor_dist_list[0]['MASS'])
	flipped_gamma_arr = np.flip(lor_dist_list[0]['GAMMA'])

	# Cumulative mass
	masscum = np.cumsum(flipped_mass_arr)
	massfraccum = masscum/masscum[-1]

	# Plot distribution as a function of the mass fraction
	line_mass_frac, = ax[1].step(massfraccum,flipped_gamma_arr,where='pre',linestyle=linestyle,label=label)
	ax[1].set_ylim(0)

	# Zoomed in version of the distribution as a function of the mass fraction
	ax_zoom = ax[1].twinx()
	line_mass_frac_zoom, = ax_zoom.step(massfraccum,flipped_gamma_arr,where='pre',linestyle=linestyle,label=label,color="C1")
	ax_zoom.set_ylim(0,50)

	if xlabel is True:
		ax[0].set_xlabel('Initial Ejection Time (sec)',fontsize=fontsize,fontweight=fontweight)
		ax[1].set_xlabel(r'M/M$_{tot}$',fontsize=fontsize,fontweight=fontweight)
	if ylabel is True:
		ax[0].set_ylabel(r'$\Gamma$',fontsize=fontsize,fontweight=fontweight)
		ax[1].set_ylabel(r'$\Gamma$',fontsize=fontsize,fontweight=fontweight)

	ax[0].set_title("Time = {} sec".format(lor_time_list[0]),fontsize=fontsize,fontweight=fontweight)

	plot_aesthetics(ax[0],fontsize=fontsize,fontweight=fontweight)
	plot_aesthetics(ax[1],fontsize=fontsize,fontweight=fontweight)
	plot_aesthetics(ax_zoom,fontsize=fontsize,fontweight=fontweight)
	
	if label is not None:
		ax[0].legend(fontsize=fontsize)

	ind = np.array([0])

	def update(i):

		ind[0] = i
		
		# Update shell index plot 
		line_shell_ind.set_xdata(lor_dist_list[ind[0]]['TE'])
		line_shell_ind.set_ydata(lor_dist_list[ind[0]]['GAMMA'])

		# Update cumulative mass fraction plot 
		flipped_mass_arr = np.flip(lor_dist_list[ind[0]]['MASS'])
		flipped_gamma_arr = np.flip(lor_dist_list[ind[0]]['GAMMA'])
		# Cumulative mass
		masscum = np.cumsum(flipped_mass_arr)
		massfraccum = masscum/masscum[-1]
		line_mass_frac.set_xdata(massfraccum)
		line_mass_frac.set_ydata(flipped_gamma_arr)

		line_mass_frac_zoom.set_xdata(massfraccum)
		line_mass_frac_zoom.set_ydata(flipped_gamma_arr)

		ax[0].set_title("Time = {} sec".format(lor_time_list[ind[0]]),fontsize=fontsize,fontweight=fontweight)

		# Redraw the figure to implement updates
		# ax[0].redraw_in_frame()
		# ax[1].redraw_in_frame()
		fig.canvas.draw_idle()

	ani = FuncAnimation(fig=fig, func=update, frames=len(lor_dist_list) ,interval=400)

	if save_pref is not None :
		ani.save('figs/{}-lorentz-dist-anim.gif'.format(save_pref))

	return ani


##############################################################################################################################

def load_lor_dist(file_name, string_match = "// Next step\n"):
	"""
	Method to load Lorentz factor distribution from the file specified by "file_name"

	The Lorentz distribution file must contain the columns: 
	RADIUS - Radius of the shell
	GAMMA - Lorentz factor of the shell
	MASS - Mass of the shell
	TE - Time of emission of the shell
	STATUS - Status of the shell, this is used by the simulation code to indicate if a shell is still active or not. 
	
	Attributes:
	separator_string = the string between each snapshot of the Lorentz distribution
	"""
	
	# Function to find all line numbers that match the "string_match" input argument
	def lines_that_equal(string, fp):
		line_num_list = [] # List to store line numbers
		line_num = 0 # Temporary line number holder
		for line in fp:
			line_num +=1
			if line == string:
				# If the line matches, append the line number to the line number list
				line_num_list.append(line_num)
		line_num_list.append(line_num) # Append last line, this is used to indicate end of file when loading data
		return line_num_list

	# With the input file open, use the lines_that_equal function to find line numbers that match the "string_match" argument
	line_num_list = 0
	with open(file_name, "r") as fp:
		line_num_list = lines_that_equal(string_match,fp)

	# For all the data between each line number in the line_num_list, load the data and append it to the data_list
	data_time = []
	data_list = []
	for i in range(len(line_num_list)-1):
		
		# Read the time at which this data occurred in the simulation
		tmp_time = np.genfromtxt(file_name,skip_header=line_num_list[i],max_rows=1)
		data_time.append(tmp_time) 
		
		# Read data
		tmp_data = np.genfromtxt(file_name,skip_header=line_num_list[i]+1,max_rows=line_num_list[i+1]-2-line_num_list[i], dtype=[("RADIUS",float),("GAMMA",float),("MASS",float),("TE",float),("STATUS",float)])
		data_list.append(tmp_data[tmp_data['STATUS']>0])

	return data_time, data_list

##############################################################################################################################

def plot_spec(file_name, z=0, joined=False, label = None, color="C0", ax=None, nuFnu=True, unc=False, Emin=None, Emax=None, save_pref=None,fontsize=14,fontweight='bold',linestyle="solid",norm=1,alpha=1):
	"""
	Method to plot the input spectrum data files

	Attributes:
	file_name = file name which contains spectrum data points 
	z = redshift to shift the spectrum to
	joined = boolean, indicates whether the points are joined or not.
	label = optional label for the plotted spectra 
	ax = the matplotlib.pyplot.axes instance to make the plot on
	
	nuFnu = boolean, indicates whether the spectrum should be a count spectrum or energy density spectrum
	unc = boolean, indicates whether to include uncertainty bars on the data points 
	Emin, Emax = indicates the minimum and maximum energy range to plot. If None is supplied, the minimum and maximum energies of the supplied data files are used

	save_pref = if not left as None, the plot will be saved and the file name will have this prefix
	xlabel, ylabel = indicate whether x- and y- labels should be included (boolean)
	fontsize, fontweight = fontsize and fontweight of the plot font and labels on the plot
	linestyle = style of the plotting line 
	"""

	# Make plot instance if it doesn't exist
	if ax is None:
		ax = plt.figure().gca()

	# Load spectrum data
	spec_data = np.genfromtxt(file_name,dtype=[("ENERG",float),("RATE",float),('UNC',float)])

	spec_data['ENERG'] /= (1+z)
	spec_data['RATE'] /= (4*np.pi*lum_dis(z)**2)
	spec_data['UNC'] /= (1+z)

	if joined is True:
		# Plot spectrum data
		if nuFnu is True:
			if unc is True:
				line = ax.errorbar(x=spec_data['ENERG'],y=norm*spec_data['RATE']*(spec_data['ENERG']**2),yerr=spec_data['UNC']*(spec_data['ENERG']**2),label=label,color=color,alpha=alpha)
			else:
				line, = ax.plot(spec_data['ENERG'],norm*spec_data['RATE']*(spec_data['ENERG']**2),label=label,color=color,linestyle=linestyle,alpha=alpha)
		else:
			if unc is True:
				line = ax.errorbar(x=spec_data['ENERG'],y=norm*spec_data['RATE'],yerr=spec_data['UNC'],label=label,color=color,alpha=alpha)
			else:
				line, = ax.plot(spec_data['ENERG'],norm*spec_data['RATE'],label=label,color=color,linestyle=linestyle,alpha=alpha)
	else:
		# Plot spectrum data
		if nuFnu is True:
			if unc is True:
				line = ax.errorbar(x=spec_data['ENERG'],y=norm*spec_data['RATE']*(spec_data['ENERG']**2),yerr=spec_data['UNC']*(spec_data['ENERG']**2),label=label,fmt=" ",marker="+",color=color,alpha=alpha)
			else:
				line = ax.errorbar(x=spec_data['ENERG'],y=norm*spec_data['RATE']*(spec_data['ENERG']**2),label=label,fmt=" ",marker="+",color=color,alpha=alpha)
		else:
			if unc is True:
				line = ax.errorbar(x=spec_data['ENERG'],y=norm*spec_data['RATE'],yerr=spec_data['UNC'],label=label,fmt=" ",marker="+",color=color,alpha=alpha)
			else:
				line = ax.errorbar(x=spec_data['ENERG'],y=norm*spec_data['RATE'],label=label,fmt=" ",marker="+",color=color,alpha=alpha)

	# Plot aesthetics
	ax.set_xscale('log')
	ax.set_yscale('log')

	# Force lower bound
	# ax.set_ylim(1e48,1e52)

	# For axis labels
	ax.set_xlabel('E (keV)',fontsize=fontsize,fontweight=fontweight)

	if nuFnu is True:
		if z > 0:
			ax.set_ylabel(r'$\nu$F$_\nu$ erg sec$^{-1}$ cm$^{-2}$ keV$^{-2}$',fontsize=fontsize,fontweight=fontweight)
		else:
			ax.set_ylabel(r'$\nu$F$_\nu$ erg sec$^{-1}$ keV$^{-2}$',fontsize=fontsize,fontweight=fontweight)
	else:
		if z > 0:
			ax.set_ylabel( r"N(E) counts sec$^{-1}$ cm$^{-2}$ keV$^{-1}$",fontsize=fontsize,fontweight=fontweight)
		else:
			ax.set_ylabel( r"N(E) counts sec$^{-1}$ keV$^{-1}$",fontsize=fontsize,fontweight=fontweight)

	# curr_ymin, curr_ymax = ax.get_ylim()
	# ax.set_ylim(curr_ymin,curr_ymax)
	# ax.set_xlim(Emin,Emax)

	# Add label names to plot if supplied
	if label is not None:
		ax.legend(fontsize=fontsize-2)

	plot_aesthetics(ax,fontsize=fontsize,fontweight=fontweight)
	
	plt.tight_layout()
	if save_pref is not None:
		plt.savefig('figs/{}-spectrum.png'.format(save_pref))	

	return line

##############################################################################################################################

def add_FermiGBM_band(ax,fontsize=12,axis="x"):
	"""
	Method to add two shaded boxes to indicate the Fermi/GBM (NaI and BGO) observation bands to a matplotlib.pyplot.axes instance

	Attributes:
	axis = Defines which axis the energy axis (in keV)
	"""

	# Grab the current ymin and ymax, this is used to set the lower and upper bounds of the vertical lines which indicate instrument observation energy range
	curr_ymin, curr_ymax = ax.get_ylim()
	curr_xmin, curr_xmax = ax.get_xlim()

	# Vertical axis
	if(axis == "x"):
		# Display Fermi/GBM - NAI energy band
		ax.axvspan(xmin=8,xmax=1e3,ymin=0.5,alpha=0.4,facecolor='grey',label='Fermi/GBM-NAI')

		# Display Fermi/GBM - BGO energy band
		ax.axvspan(xmin=150,xmax=3*1e4,ymin=0.5,alpha=0.4,facecolor='orange',label='Fermi/GBM-BGO')

	# Horizontal axis
	elif(axis == "y"):
		# Display Fermi/GBM - NAI energy band
		ax.axhspan(ymin=8,ymax=1e3,alpha=0.4,facecolor='grey',label='Fermi/GBM-NAI')

		# Display Fermi/GBM - BGO energy band
		ax.axhspan(ymin=150,ymax=3*1e4,alpha=0.4,facecolor='orange',label='Fermi/GBM-BGO')


	# Add to legend	
	ax.legend(fontsize=fontsize)

	# We don't want the plotting window to change if either of the energy band edges do not overlap with the plotted energy spectra
	ax.set_ylim(curr_ymin,curr_ymax)
	ax.set_xlim(curr_xmin,curr_xmax)

##############################################################################################################################

def add_SwiftBAT_band(ax,fontsize=12,axis="x"):
	"""
	Method to add two shaded boxes to indicate the Swift/BAT observation band to a matplotlib.pyplot.axes instance

	Attributes:
	axis = Defines which axis the energy axis (in keV)
	"""

	# Grab the current ymin and ymax, this is used to set the lower and upper bounds of the vertical lines which indicate instrument observation energy range
	curr_ymin, curr_ymax = ax.get_ylim()
	curr_xmin, curr_xmax = ax.get_xlim()

	# Display Swift/BAT energy band

	# Vertical axis
	if(axis == "x"):
		ax.axvspan(xmin=5,xmax=350,ymin=0.5,alpha=0.4,facecolor='blue',label='Swift/BAT')

	# Horizontal axis
	elif(axis == "y"):
		ax.axhspan(ymin=5,ymax=350,alpha=0.4,facecolor='blue',label='Swift/BAT')

	# Add to legend	
	ax.legend(fontsize=fontsize)

	# We don't want the plotting window to change if either of the energy band edges do not overlap with the plotted energy spectra
	ax.set_ylim(curr_ymin,curr_ymax)
	ax.set_xlim(curr_xmin,curr_xmax)

##############################################################################################################################

def plot_light_curve(file_name, z=0, label=None, ax=None, fig = None, Tmin=None, Tmax=None, save_pref=None,color="C0", alpha=1, fontsize=14,fontweight='bold', logscale=False,y_factor=1,guidelines=False,xax_units="s"):
	"""
	Method to plot the input light curve data files

	Attributes:
	file_name = file name which contains spectrum data points 
	z = redshift to shift the light curve to
	label = optional label for the plotted light curve 
	ax = the matplotlib.pyplot.axes instance to make the plot on
	
	Tmin, Tmax = indicates the minimum and maximum time range to plot. If None is supplied, the minimum and maximum times of the supplied data files are used

	save_pref = if not left as None, the plot will be saved and the file name will have this prefix
	xlabel, ylabel = indicate whether x- and y- labels should be included (boolean)
	fontsize, fontweight = fontsize and fontweight of the plot font and labels on the plot
	linestyle = style of the plotting line 
	logscale = boolean, Indicates whether the time x- and y- axes should be in log scale 

	xax_units = "s", indicates the units of the x axis on the light curve. ("s"==seconds, "m"==minutes, "h"==hours, d=="days")
	"""

	if(z<0):
		print("Please provide a non-negative redshift.")
		return;
	else:
		# Make plot instance if it doesn't exist
		if fig is None:
			fig = plt.figure() 
		if ax is None:
			ax = fig.gca()

		# Load light curve data
		light_curve_data = np.genfromtxt(file_name,dtype=[("TIME",float),("RATE",float)])

		# Unit conversion
		x_conv = 1 # if xax_unit == "s", then we don't have to change anything
		if(xax_units == "m"):
			x_conv = 60 # if xax_unit == "m"
		if(xax_units == "h"):
			x_conv = 60*60 # if xax_unit == "h" 
		if(xax_units == "d"):
			x_conv = 60*60*24 # if xax_unit == "d"

		light_curve_data['TIME']/=x_conv

		# Plot light curve data

		if(z>0):
			# ax.scatter(light_curve_data['TIME']*(1+z),light_curve_data['RATE']/(4*np.pi*lum_dis(z)**2),label=label,marker=".")
			ax.step(light_curve_data['TIME']*(1+z),light_curve_data['RATE']*y_factor/(4*np.pi*lum_dis(z)**2),label=label,marker=" ",where="mid",color=color,alpha=alpha)
		else: 
			# If z = 0, return luminosity
			# ax.scatter(light_curve_data['TIME'],light_curve_data['RATE'],label=label,marker=".")
			ax.step(light_curve_data['TIME'],light_curve_data['RATE']*y_factor,label=label,marker=" ",where="mid",color=color,alpha=alpha)

		if guidelines is True:
			# rhowindline = lambda t, t0, norm: norm*np.power(t/t0,-5./4.)
			# rhoconstline = lambda t, t0, norm: norm*np.power(t/t0,-11./8.)

			p = 2.2
			bjbline = lambda t, t0, norm: norm*np.power(t/t0,-0.9)
			ajbline = lambda t, t0, norm: norm*np.power(t/t0,-1.5)

			tstart = np.log10( light_curve_data['TIME'][0] )
			tstop = np.log10( light_curve_data['TIME'][-1] )
			tspace = np.logspace(start = tstart, stop= tstop)

			index_max = np.argmax(light_curve_data['RATE'])

			# g_norm_wind = rhowindline(tstart,light_curve_data['TIME'][index_max],light_curve_data['RATE'][index_max])
			# g_norm_const = rhoconstline(tstart,light_curve_data['TIME'][index_max],light_curve_data['RATE'][index_max])
			g_bjb_norm = bjbline(tstart,light_curve_data['TIME'][index_max+30],light_curve_data['RATE'][index_max])*1.2
			g_ajb_norm = ajbline(tstart,light_curve_data['TIME'][index_max+140],light_curve_data['RATE'][index_max+150])*1.4

			# ax.plot(tspace,rhowindline(tspace,tstart,g_norm_wind),label=r"$t^{-5/4}$",color='r')
			# ax.plot(tspace,rhoconstline(tspace,tstart,g_norm_const),label=r"$t^{-11/8}$",color='k')
			ax.plot(tspace,bjbline(tspace,tstart,g_bjb_norm),label=r"$t^{-0.9}$",color='r')
			ax.plot(tspace,ajbline(tspace,tstart,g_ajb_norm),label=r"$t^{-1.5}$",color='g')

		# Custom power law index annotation
		annot = ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points", bbox=dict(boxstyle="round", fc="w"),arrowprops=dict(arrowstyle="->"))

		if(logscale == True):
			ax.set_yscale('log')
			ax.set_xscale('log')

		# Plot aesthetics
		# For axis labels
		if(z>0):
			ax.set_ylabel(r'Rate (ph cm$^{-2}$ s$^{-1}$)',fontsize=fontsize,fontweight=fontweight)
		else:
			ax.set_ylabel(r'Rate (ph s$^{-1}$)',fontsize=fontsize,fontweight=fontweight)

		if(xax_units == "s"):
			ax.set_xlabel('Obs Time (sec)',fontsize=fontsize,fontweight=fontweight)
		if(xax_units == "m"):
			ax.set_xlabel('Obs Time (minutes)',fontsize=fontsize,fontweight=fontweight)
		if(xax_units == "h"):
			ax.set_xlabel('Obs Time (hours)',fontsize=fontsize,fontweight=fontweight)
		if(xax_units == "d"):
			ax.set_xlabel('Obs Time (days)',fontsize=fontsize,fontweight=fontweight)
		

		# Add label names to plot if supplied
		if label is not None:
			plt.legend(fontsize=fontsize-2)

		plot_aesthetics(ax,fontsize=fontsize,fontweight=fontweight)
		
		plt.tight_layout()


		def onclick(event, points):
			"""
			Function used to making a line and calculating the power law index of the line
			"""

			# If this is the first point being clicked on, add it to the list of points
			if len(points) == 0:
				points.append([event.xdata, event.ydata])
			# If this is the second point being clicked on, add it to the list of points, make the connecting line, and show the power law index
			elif len(points) == 1:
				# Append points to list
				points.append([event.xdata, event.ydata])

				# Make connecting line
				ax.plot([points[0][0] , points[1][0]] ,[points[0][1], points[1][1]],color="m")

				# Calculate the power law index
				ratio_F = points[1][1]/points[0][1] # Ratio of flux 
				ratio_E = points[1][0]/points[0][0] # Ratio of energy
				alpha = (np.log(ratio_F) / np.log(ratio_E) )

				# Set the position of the annotation and make it visible
				annot.xy = points[1]
				annot.set(visible = True)

				# Display the point index
				text = r"$\alpha$ = {}".format(alpha)
				annot.set_text(text)

			# If this is the third point selected, remove the line and reset the points
			elif len(points) == 2:
				# Remove the line
				ax.lines[-1].remove()

				# Hide the annotation
				annot.set(visible = False)

				# Reset points list
				points.clear()


			# Redraw the figure to implement updates
			ax.redraw_in_frame()
			fig.canvas.draw_idle()


		# Call function for making line between two points
		points = []
		fig.canvas.mpl_connect('button_press_event', lambda event: onclick(event, points) )

		if save_pref is not None:
			plt.savefig('figs/{}-light-curve.png'.format(save_pref))

		return fig

##############################################################################################################################

def plot_light_curve_interactive(init_Tmin, init_Tmax, init_dT, init_Emin, init_Emax, z=0, 
	with_comps=False, label=None, label_comps=True, ax=None, save_pref=None, fontsize=14,fontweight='bold',logscale=False,with_gbm=False):
	"""
	Method to plot the input light curve data files (interactively!)

	init_Tmin, init_Tmax 
			= Sets the initial time selection interval for calculating the spectrum and also sets the initial time window for the light curve.
			In addition, this will set the largest time interval the light curve will be displayed in.
	init_Emin, init_Emax
			= Sets the initial energy selection interval for calculating the light curve and also sets the initial energy window for the spectrum.
			In addition, this will set the largest energy interval the spectrum will be displayed in.

	z = float > 0, redshift
	with_comps = boolean, indicates whether the individual components should be displayed
	
	label = optional label for the plotted light curve 
	fontsize, fontweight = fontsize and fontweight of the plot font and labels on the plot
	logscale = boolean, Indicates whether the time x- and y- axes should be in log scale 
	"""

	comp_indicator = "false"
	if(with_comps == True):
		comp_indicator = "true"
	num_comps = 4
	comp_suff = ["TH","IS","FS","RS"]
	comp_labels = [None,None,None,None]
	if (label_comps == True):
		comp_labels = comp_suff
	comp_colors = ['r','C0','C1','C2']

	if(z<0):
		print("Please provide a non-negative redshift.")
		return;
	
	# Make initial data
	subprocess.run(["./main","timechange", comp_indicator, "{}".format(logscale), "{}".format(init_Tmin/(1+z)), "{}".format(init_Tmax/(1+z)), "{}".format(init_Emin*(1+z)), "{}".format(init_Emax*(1+z)) ])
	subprocess.run(["./main","energychange", comp_indicator, "{}".format(logscale), "{}".format(init_Tmin/(1+z)), "{}".format(init_Tmax/(1+z)), "{}".format(init_dT/(1+z)), "{}".format(init_Emin*(1+z)), "{}".format(init_Emax*(1+z)) ])

	# Make plot instance if it doesn't exist
	fig, ax = plt.subplots(1,2,figsize=(16, 8))	
	
	# Load initial light curve data
	lc_data_tot = np.genfromtxt("data-file-dir/quickplot_light_curve.txt",dtype=[("TIME",float),("RATE",float)])

	# Plot initial light curve
	if(z>0):
		lc_tot_line, = ax[0].step(lc_data_tot['TIME']*(1+z),lc_data_tot['RATE']/(4*np.pi*lum_dis(z)**2),label=label,marker=" ",where="mid",color="k")
		ax[0].set_ylabel(r'Rate (ph cm$^{-2}$ s$^{-1}$)',fontsize=fontsize,fontweight=fontweight)
	else:
		# If z = 0, return luminosity
		lc_tot_line, = ax[0].step(lc_data_tot['TIME'],lc_data_tot['RATE'],label=label,marker=" ",where="mid",color="k")
		ax[0].set_ylabel(r'Rate (ph s$^{-1}$)',fontsize=fontsize,fontweight=fontweight)

	if(logscale == True):
		ax[0].set_yscale('log')
		ax[0].set_xscale('log')
	ax[0].set_xlabel('Obs Time (sec)',fontsize=fontsize,fontweight=fontweight)
	plot_aesthetics(ax[0],fontsize=fontsize,fontweight=fontweight)

	# If components are desired
	if(with_comps == True):
		# Load component data
		lc_comp_data = [0] * num_comps
		for i in range(num_comps):
			lc_comp_data[i] = np.genfromtxt("data-file-dir/quickplot_light_curve_{}.txt".format(comp_suff[i]),dtype=[("TIME",float),("RATE",float)])

		# Plot component light curves
		lc_comp_lines = [0] * num_comps
		if(z>0):
			for i in range(num_comps):
				lc_comp_lines[i], = ax[0].step(lc_comp_data[i]['TIME']*(1+z),lc_comp_data[i]['RATE']/(4*np.pi*lum_dis(z)**2),color=comp_colors[i],marker=" ",where="mid")
		else: 
			# If z = 0, return luminosity
			for i in range(num_comps):
				lc_comp_lines[i], = ax[0].step(lc_comp_data[i]['TIME'],lc_comp_data[i]['RATE'],color=comp_colors[i],marker=" ",where="mid")



	# Plot initial spectrum 
	spec_tot_line = plot_spec("data-file-dir/quickplot_spectrum.txt",ax=ax[1],z=z,joined=True,color='k',label=label)
	# If components are desired, plot initial component spectra 
	if(with_comps == True):
		spec_comp_lines = [0] * num_comps
		for i in range(num_comps):
			spec_comp_lines[i] = plot_spec("data-file-dir/quickplot_spectrum_{}.txt".format(comp_suff[i]),ax=ax[1],z=z,joined=True,color=comp_colors[i],label=comp_labels[i])
	
	if(with_gbm == True):
		add_FermiGBM_band(ax[1])

	# Display time selection interval
	selected_Tmin_line = ax[0].axvline(x=init_Tmin,color='k')
	selected_Tmax_line = ax[0].axvline(x=init_Tmax,color='k')

	# Display energy selection interval on plot
	selected_Emin_line = ax[1].axvline(x=init_Emin,color='k')
	selected_Emax_line = ax[1].axvline(x=init_Emax,color='k')

	# Shade in selected region of light curve
	shaded_region_time = ax[0].axvspan(xmin=init_Tmin,xmax=init_Tmax,alpha=0.1,facecolor='C0',zorder=0)
	# And spectrum 
	shaded_region_energy = ax[1].axvspan(xmin=init_Emin,xmax=init_Emax,alpha=0.1,facecolor='C0',zorder=0)
	

	# Initialize the text boxes environment
	fig.canvas.mpl_disconnect(fig.canvas.manager.key_press_handler_id)
	
	# Make time selection and time window text boxes
	axbox_time_select = plt.axes([0.2, 0.125, 0.1, 0.04])
	txtbox_time_select = TextBox(ax=axbox_time_select, label='Time Selection', initial="{0:.2f}, {1:.2f}".format(init_Tmin, init_Tmax) )

	axbox_time_window = plt.axes([0.2, 0.08, 0.1, 0.04])
	txtbox_time_window = TextBox(ax=axbox_time_window, label='Time Window', initial="{0:.2f}, {1:.2f}".format(init_Tmin, init_Tmax) )

	# Make time resolution selection box
	axbox_time_res_select = plt.axes([0.2, 0.035, 0.1, 0.04])
	txtbox_time_res_select = TextBox(ax=axbox_time_res_select, label='Time Resolution', initial="{0:.2f}".format(init_dT) )

	# Make energy selection and energy window text boxes
	axbox_energy_select = plt.axes([0.65, 0.125, 0.1, 0.04])
	txtbox_energy_select = TextBox(ax=axbox_energy_select, label='Energy Selection', initial="{0:.2f}, {1:.2f}".format(init_Emin,init_Emax) )

	axbox_energy_window = plt.axes([0.65, 0.08, 0.1, 0.04])
	txtbox_energy_window = TextBox(ax=axbox_energy_window, label='Energy Window', initial="{0:.2f}, {1:.2f}".format(init_Emin,init_Emax) )

	# Redshift selection text box
	axbox_redshift = plt.axes([0.65, 0.035, 0.1, 0.04])
	txtbox_redshift = TextBox(ax=axbox_redshift, label='Redshift', initial="{0:.2f}".format(z) )

	# Custom power law index annotation
	annot = ax[1].annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points", bbox=dict(boxstyle="round", fc="w"),arrowprops=dict(arrowstyle="->"))

	# Make update functions
	
	def submit_time_select(val,z):
		"""
		Function call when a time selection is given, this will alter the displayed spectra
		"""
		# val will be separated into two values, split by the comma
		x = val.split(", ")

		selected_Tmin = float(x[0])
		selected_Tmax = float(x[1])

		# Update the time selection indicating lines
		selected_Tmin_line.set_xdata(selected_Tmin)
		selected_Tmax_line.set_xdata(selected_Tmax)

		# Updated shaded in selected region of light curve
		shaded_region_time.xy = [[ selected_Tmin, 0.], [ selected_Tmin, 1.], [selected_Tmax, 1.], [selected_Tmax, 0.], [ selected_Tmin, 0.]]

		# Compute the new spectrum for this time selection
		subprocess.run(["./main","timechange", comp_indicator, "{}".format(logscale), "{}".format(selected_Tmin/(1+z)), "{}".format(selected_Tmax/(1+z)), "{}".format(init_Emin*(1+z)), "{}".format(init_Emax*(1+z)) ])

		# If components are desired, plot initial component spectra 
		if(with_comps == True):
			for i in range(num_comps):
				# Load component spectra data
				tmp_comp_data = np.genfromtxt("data-file-dir/quickplot_spectrum_{}.txt".format(comp_suff[i]),dtype=[("ENERGY",float),("RATE",float),("UNC",float)])
				# Update plotted data 
				spec_comp_lines[i].set_xdata(tmp_comp_data['ENERGY']/(1+z))
				spec_comp_lines[i].set_ydata(tmp_comp_data['RATE'] * tmp_comp_data['ENERGY']**2 )

		# Load spectrum data
		tmp_comp_data = np.genfromtxt("data-file-dir/quickplot_spectrum.txt",dtype=[("ENERGY",float),("RATE",float),("UNC",float)])
		# Update plotted spectrum data
		spec_tot_line.set_xdata(tmp_comp_data['ENERGY']/(1+z))
		spec_tot_line.set_ydata(tmp_comp_data['RATE']* tmp_comp_data['ENERGY']**2)

		# Redraw the figure to implement updates
		ax[0].redraw_in_frame()
		ax[1].redraw_in_frame()
		fig.canvas.draw_idle()
	
	def submit_energy_select(val,z):
		"""
		Function call when a energy selection is given, this will edit the observed light curve 
		"""

		# val will be separated into two values, split by the comma
		x = val.split(", ")

		selected_Emin = float(x[0])
		selected_Emax = float(x[1])

		# Update the energy selection indicating lines
		selected_Emin_line.set_xdata(selected_Emin)
		selected_Emax_line.set_xdata(selected_Emax)

		# Updated shaded in selected region of light curve
		shaded_region_energy.xy = [[ selected_Emin, 0.], [ selected_Emin, 1.], [selected_Emax, 1.], [selected_Emax, 0.], [ selected_Emin, 0.]]

		# Compute the new light curve for this energy selection
		subprocess.run(["./main","energychange", comp_indicator, "{}".format(logscale), "{}".format(init_Tmin/(1+z)), "{}".format(init_Tmax/(1+z)), "{}".format(init_dT/(1+z)), "{}".format(selected_Emin*(1+z)), "{}".format(selected_Emax*(1+z)) ])

		# If components are desired, plot initial component spectra 
		if(with_comps == True):
			for i in range(num_comps):
				# Load component light curve data
				tmp_comp_data = np.genfromtxt("data-file-dir/quickplot_light_curve_{}.txt".format(comp_suff[i]),dtype=[("TIME",float),("RATE",float)])
				# Update plotted data 
				if(z>0):
					lc_comp_lines[i].set_xdata(tmp_comp_data['TIME']*(1+z))
					lc_comp_lines[i].set_ydata(tmp_comp_data['RATE']/(4*np.pi*lum_dis(z)**2))
				else:
					lc_comp_lines[i].set_xdata(tmp_comp_data['TIME'])
					lc_comp_lines[i].set_ydata(tmp_comp_data['RATE'])
		# Load light curve data
		tmp_comp_data = np.genfromtxt("data-file-dir/quickplot_light_curve.txt",dtype=[("TIME",float),("RATE",float)])
		# Update plotted spectrum data
		if(z>0):
			lc_tot_line.set_xdata(tmp_comp_data['TIME']*(1+z))
			lc_tot_line.set_ydata(tmp_comp_data['RATE']/(4*np.pi*lum_dis(z)**2))
		else:
			lc_tot_line.set_xdata(tmp_comp_data['TIME'])
			lc_tot_line.set_ydata(tmp_comp_data['RATE'])


		# Redraw the figure to implement updates
		ax[0].redraw_in_frame()
		ax[1].redraw_in_frame()
		fig.canvas.draw_idle()

	def submit_time_res_select(val):
		"""
		Function call when a new time resolution is given, this will edit the observed light curve time resolution
		"""

		# Compute the new light curve for this energy selection
		subprocess.run(["./main","energychange", comp_indicator, "{}".format(logscale), "{}".format(init_Tmin/(1+z)), "{}".format(init_Tmax/(1+z)), "{}".format(val/(1+z)), "{}".format(init_Emin*(1+z)), "{}".format(init_Emax*(1+z)) ])

		# If components are desired, plot initial component spectra 
		if(with_comps == True):
			for i in range(num_comps):
				# Load component light curve data
				tmp_comp_data = np.genfromtxt("data-file-dir/quickplot_light_curve_{}.txt".format(comp_suff[i]),dtype=[("TIME",float),("RATE",float)])
				# Update plotted data 
				if(z>0):
					lc_comp_lines[i].set_xdata(tmp_comp_data['TIME']*(1+z))
					lc_comp_lines[i].set_ydata(tmp_comp_data['RATE']/(4*np.pi*lum_dis(z)**2))
				else:
					lc_comp_lines[i].set_xdata(tmp_comp_data['TIME'])
					lc_comp_lines[i].set_ydata(tmp_comp_data['RATE'])
		# Load light curve data
		tmp_comp_data = np.genfromtxt("data-file-dir/quickplot_light_curve.txt",dtype=[("TIME",float),("RATE",float)])
		# Update plotted spectrum data
		if(z>0):
			lc_tot_line.set_xdata(tmp_comp_data['TIME']*(1+z))
			lc_tot_line.set_ydata(tmp_comp_data['RATE']/(4*np.pi*lum_dis(z)**2))
		else:
			lc_tot_line.set_xdata(tmp_comp_data['TIME'])
			lc_tot_line.set_ydata(tmp_comp_data['RATE'])


		# Redraw the figure to implement updates
		ax[0].redraw_in_frame()
		ax[1].redraw_in_frame()
		fig.canvas.draw_idle()

	def submit_time_window(val):
		"""
		Function call when a time window is given
		"""
		# val will be separated into two values, split by the comma
		x = val.split(", ")

		window_Tmin = float(x[0])
		window_Tmax = float(x[1])

		# Update the time window
		ax[0].set_xlim(window_Tmin,window_Tmax)

		# Redraw the figure to implement updates
		ax[0].redraw_in_frame()
		ax[1].redraw_in_frame()
		fig.canvas.draw_idle()
		
	def submit_energy_window(val):
		"""
		Function call when a energy window is given
		"""
		# val will be separated into two values, split by the comma
		x = val.split(", ")

		window_Emin = float(x[0])
		window_Emax = float(x[1])

		# Update the energy window
		ax[1].set_xlim(window_Emin,window_Emax)

		# Redraw the figure to implement updates
		ax[0].redraw_in_frame()
		ax[1].redraw_in_frame()
		fig.canvas.draw_idle()

	def submit_redshift(val):
		"""
		Function to call when a new redshift is input by the user.
		"""
		new_z = float(val)
		# Remake spectrum (same time interval, but now different enclosed emission)
		submit_energy_select("{}, {}".format(init_Emin,init_Emax),new_z)

		# # Remake light curve (same energy interval, but now spectrum is shifted) 
		submit_time_select("{}, {}".format(init_Tmin,init_Tmax),new_z)


	def onclick(event, points):
		"""
		Function used to making a line and calculating the power law index of the line
		"""

		# If this is the first point being clicked on, add it to the list of points
		if len(points) == 0:
			points.append([event.xdata, event.ydata])
		# If this is the second point being clicked on, add it to the list of points, make the connecting line, and show the power law index
		elif len(points) == 1:
			# Append points to list
			points.append([event.xdata, event.ydata])

			# Make connecting line
			ax[1].plot([points[0][0] , points[1][0]] ,[points[0][1], points[1][1]],color="m")

			# Calculate the power law index
			ratio_F = points[1][1]/points[0][1] # Ratio of flux 
			ratio_E = points[1][0]/points[0][0] # Ratio of energy
			alpha = (np.log(ratio_F) / np.log(ratio_E) ) - 2.

			# Set the position of the annotation and make it visible
			annot.xy = points[1]
			annot.set(visible = True)

			# Display the point index
			text = r"$\alpha$ = {}".format(alpha)
			annot.set_text(text)

		# If this is the third point selected, remove the line and reset the points
		elif len(points) == 2:
			# Remove the line
			ax[1].lines[-1].remove()

			# Hide the annotation
			annot.set(visible = False)

			# Reset points list
			points.clear()


		# Redraw the figure to implement updates
		ax[1].redraw_in_frame()
		fig.canvas.draw_idle()

		

	# Call functions to update selection intervals
	txtbox_time_select.on_submit(lambda val: submit_time_select(val,z))
	txtbox_energy_select.on_submit(lambda val: submit_energy_select(val,z))
	
	# Call function to change time resolution of light curve
	txtbox_time_res_select.on_submit(lambda val: submit_time_res_select(val,z))

	# Call functions to update windows
	txtbox_time_window.on_submit(submit_time_window)
	txtbox_energy_window.on_submit(submit_energy_window)

	# Call function to set a new redshift
	txtbox_redshift.on_submit(submit_redshift)

	# Call function for making line between two points
	points = []
	fig.canvas.mpl_connect('button_press_event', lambda event: onclick(event, points) )



	fig.subplots_adjust(bottom=0.25,wspace=0.4)

	# plt.tight_layout()
	if save_pref is not None:
		plt.savefig('figs/{}-light-curve.png'.format(save_pref))

	return fig, txtbox_time_select, txtbox_time_window, txtbox_energy_select, txtbox_energy_window


##############################################################################################################################

def load_therm_emission(file_name):
	"""
	Method to load thermal emission data from the given file name
	"""

	dtype = np.dtype([('TE',float),('TA',float),('DELT',float),('TEMP',float),('FLUX',float),('RPHOT',float),("SHIND",int)])

	return np.genfromtxt(file_name,dtype=dtype)

##############################################################################################################################

def load_is_emission(file_name):
	"""
	Method to load internal shock emission data from the given file name
	"""

	dtype = np.dtype([('TE',float),('TA',float),('DELT',float),('BEQ',float),('GAMMAE',float),('ESYN',float),('GAMMAR',float),('EDISS',float),("NUC",float),("NUM",float),("SHIND",int),('ASYN',float),('TAU',float),('RELVEL',float)])

	return np.genfromtxt(file_name,dtype=dtype)

##############################################################################################################################

def load_fs_emission(file_name):
	"""
	Method to load forward shock emission data from the given file name
	"""

	dtype = np.dtype([('TE',float),('TA',float),('DELT',float),('BEQ',float),('GAMMAE',float),('ESYN',float),('GAMMAR',float),('EDISS',float),("NUC",float),("NUM",float),("THETA",float),("SHIND",int)])

	return np.genfromtxt(file_name,dtype=dtype)

##############################################################################################################################

def load_rs_emission(file_name):
	"""
	Method to load reverse shock emission data from the given file name
	"""

	dtype = np.dtype([('TE',float),('TA',float),('DELT',float),('BEQ',float),('GAMMAE',float),('ESYN',float),('GAMMAR',float),('EDISS',float),("NUC",float),("NUM",float),("SHIND",int)])

	return np.genfromtxt(file_name,dtype=dtype)

##############################################################################################################################

def plot_param_vs_time(emission_comp,param,frame="obs",ax=None,z=0, y_factor=1, label=None, Tmin=None, Tmax=None,save_pref=None,fontsize=14,fontweight='bold',disp_xax=True,disp_yax=True,
	color='C0',marker='.',markersize=7,alpha=1):
	"""
	Plot emission parameters as a function of time

	Attributes:
	emission_comp = the emission data to be plotted
	param = which param to plot against the time axis
	frame = string, should be given as "obs" or "source"
		"obs" indicates that the observed time will be used 
		"source" indicate that the emitted time will be used

	ax = the matplotlib.pyplot.axes instance to make the plot on
	z = redshift to shift the light curve to
	y_factor = value to multiply the "param" axis by 

	label = optional label for the plotted light curve 
	
	Tmin, Tmax = indicates the minimum and maximum time range to plot. If None is supplied, the minimum and maximum times of the supplied data files are used

	save_pref = if not left as None, the plot will be saved and the file name will have this prefix
	fontsize, fontweight = fontsize and fontweight of the plot font and labels on the plot
	disp_xax, disp_yax = boolean, indicate whether x- and y- ticks/labels should be displayed
	color = color of the data
	marker = marker of the data
	markersize = markersize of the data marker
	alpha = transparency of the data
	"""

	time_str = "TA"
	if(frame=="source"):
		time_str = "TE"

	# Make plot instance if it doesn't exist
	if ax is None:
		ax = plt.figure().gca()

	if Tmin is None:
		Tmin = 0
	if Tmax is None:
		Tmax = np.max(emission_comp[time_str])*(1+z)

	# Multiply by 1+z for the time axis and apply the supplied factor on the y-axis 
	# Take only the time elements between Tmin and Tmax
	ax_time = emission_comp[time_str][(emission_comp[time_str]>Tmin) & (emission_comp[time_str] < Tmax)] * (1+z)

	# Multiply by input factor
	ax_param = emission_comp[param][(emission_comp[time_str]>Tmin) & (emission_comp[time_str] < Tmax)] * y_factor

	ax.scatter(x=ax_time,y=ax_param,label=label,c=color,marker=marker,s=markersize, picker=True,alpha=alpha)

	if disp_yax is True:
		ax.set_ylabel(param,fontsize=fontsize,fontweight=fontweight)
	if disp_xax is True:
		if(time_str == "TA"):
			ax.set_xlabel(r't$_a$',fontsize=fontsize,fontweight=fontweight)
		elif(time_str == "TE"):
			ax.set_xlabel(r't$_e$',fontsize=fontsize,fontweight=fontweight)

	plot_aesthetics(ax,fontsize=fontsize,fontweight=fontweight)
		
	if save_pref is not None:
		plt.savefig('figs/{}-param-{}-vs-t.png'.format(save_pref,param))

##############################################################################################################################

def plot_evo_therm(thermal_emission,frame="obs",ax=None,z=0,Tmin=None, Tmax=None,save_pref=None,fontsize=14,fontweight='bold',ylogscale=True,xlogscale=True):
	"""
	Plot evolution of thermal emission parameters

	Attributes:
	thermal_emission = the emission data to be plotted
	frame = string, should be given as "obs" or "source"
		"obs" indicates that the observed time will be used 
		"source" indicate that the emitted time will be used

	ax = the matplotlib.pyplot.axes instance to make the plot on
	z = redshift to shift the light curve to
	
	Tmin, Tmax = indicates the minimum and maximum time range to plot. If None is supplied, the minimum and maximum times of the supplied data files are used

	save_pref = if not left as None, the plot will be saved and the file name will have this prefix
	fontsize, fontweight = fontsize and fontweight of the plot font and labels on the plot
	"""

	# Make plot instance if it doesn't exist
	if ax is None:
		fig, ax = plt.subplots(2,1,figsize=(5,8))

	# Plot temperature of the thermal component vs time (in observer frame)
	plot_param_vs_time(thermal_emission,'TEMP', y_factor=kb_kev/(1+z), ax=ax[0], z=z,Tmin=Tmin, Tmax=Tmax,
		fontsize=fontsize, fontweight=fontweight, disp_xax=False, disp_yax=False,frame=frame)
	
	if(frame == "obs"):
		ax[0].set_xlabel(r't$_{obs}$ (sec)',fontsize=fontsize,fontweight=fontweight)
	if(frame == "source"):
		ax[0].set_xlabel(r't$_{e} (sec)$',fontsize=fontsize,fontweight=fontweight)
	ax[0].set_ylabel(r'k$_B$T (KeV)',fontsize=fontsize,fontweight=fontweight)
	if(ylogscale == True):
		ax[0].set_yscale('log')
	if(xlogscale == True):
		ax[0].set_xscale('log')

	# Plot Rphot vs Tphot
	# ax[1].scatter(thermal_emission['RPHOT'],thermal_emission['TEMP'])
	plot_param_vs_time(thermal_emission,'RPHOT', y_factor=3*1e10, ax=ax[1], z=z, Tmin=Tmin, Tmax=Tmax,
		fontsize=fontsize, fontweight=fontweight, disp_xax=False, disp_yax=False,frame=frame)

	if(ylogscale == True):
		ax[1].set_yscale('log')
	if(xlogscale == True):
		ax[1].set_xscale('log')

	if(frame == "obs"):
		ax[1].set_xlabel(r't$_{obs}$ (sec)',fontsize=fontsize,fontweight=fontweight)
	if(frame == "source"):
		ax[1].set_xlabel(r't$_{e} (sec)$',fontsize=fontsize,fontweight=fontweight)
	ax[1].set_ylabel(r'R$_{phot}$ (cm)',fontsize=fontsize,fontweight=fontweight)

	plot_aesthetics(ax[0],fontsize=fontsize,fontweight=fontweight)
	plot_aesthetics(ax[1],fontsize=fontsize,fontweight=fontweight)
	
	plt.tight_layout()
	if save_pref is not None:
		plt.savefig('figs/{}-thermal-evo.png'.format(save_pref))

##############################################################################################################################

def plot_evo_int_shock(is_emission,frame="obs",ax=None,z=0,Tmin=None, Tmax=None,save_pref=None,fontsize=14,fontweight='bold'):
	"""
	Plot evolution of internal shock emission parameters 

	Attributes:
	is_emission = the emission data to be plotted
	frame = string, should be given as "obs" or "source"
		"obs" indicates that the observed time will be used 
		"source" indicate that the emitted time will be used

	ax = the matplotlib.pyplot.axes instance to make the plot on
	z = redshift to shift the light curve to
	
	Tmin, Tmax = indicates the minimum and maximum time range to plot. If None is supplied, the minimum and maximum times of the supplied data files are used

	save_pref = if not left as None, the plot will be saved and the file name will have this prefix
	fontsize, fontweight = fontsize and fontweight of the plot font and labels on the plot
	"""

	if ax is None:
		fig, ax = plt.subplots(2,1,figsize=(7,8),sharex=True)
	
	# Make a copy of the axis in order to over plot two separate data sets
	ax0cp = ax[0].twinx()

	# Plot Arrival Time (ta) vs Emission Time (te)
	plot_param_vs_time(is_emission,'TE', ax=ax[0], z=z, Tmin=Tmin, Tmax=Tmax,
		fontsize=fontsize, fontweight=fontweight, disp_xax=False, disp_yax=False,marker='^',frame=frame)
	# Plot Arrival Time (ta) vs delta T
	plot_param_vs_time(is_emission,'DELT', ax=ax0cp, z=z,Tmin=Tmin, Tmax=Tmax,
		fontsize=fontsize, fontweight=fontweight, disp_xax=False, disp_yax=False,marker='.',color='C1',frame=frame)
	
	ax[0].set_ylabel(r'$t_{e}$',fontsize=fontsize,fontweight=fontweight)
	ax0cp.set_ylabel(r'$\Delta t$',fontsize=fontsize,fontweight=fontweight)
	ax0cp.yaxis.set_label_position("right")
	ax0cp.yaxis.tick_right()

	# Make a copy of the axis in order to over plot two separate data sets
	ax1cp = ax[1].twinx()
	
	# Plot Arrival Time (ta) vs the dissipated energy (e)
	plot_param_vs_time(is_emission,'EDISS', ax=ax[1], y_factor=is_emission['DELT'], z=z, Tmin=Tmin, Tmax=Tmax,
		fontsize=fontsize, fontweight=fontweight, disp_xax=False, disp_yax=False,marker='^',frame=frame)
	# Plot Arrival Time (ta) vs approximate Lorentz factor (gamma_r)
	plot_param_vs_time(is_emission,'GAMMAR', ax=ax1cp, y_factor=1/100, z=z,Tmin=Tmin, Tmax=Tmax,
		fontsize=fontsize, fontweight=fontweight, disp_xax=False, disp_yax=False,marker='.',color='C1',frame=frame)

	ax[1].set_ylabel(r'E$_{diss}/\Delta$t$_e$',fontsize=fontsize,fontweight=fontweight)
	if(frame == "obs"):
		ax[1].set_xlabel(r't$_{obs}$ (sec)',fontsize=fontsize,fontweight=fontweight)
	if(frame == "source"):
		ax[1].set_xlabel(r't$_{e} (sec)$',fontsize=fontsize,fontweight=fontweight)
	ax1cp.set_ylabel(r'$\Gamma_{r}/100$',fontsize=fontsize,fontweight=fontweight)
	ax1cp.yaxis.set_label_position("right")
	ax1cp.yaxis.tick_right()
	
	ax[0].set_ylim(-0.25*10**5,6.25*10**5)
	ax0cp.set_ylim(-0.2,4.2)
	ax[1].set_xlim(-1)
	ax1cp.set_ylim(-0.2,4.2)

	ax[0].grid(axis='x')
	ax[1].grid(axis='x')

	for i in range(2):
		plot_aesthetics(ax[i],fontsize=fontsize,fontweight=fontweight)
	for twin in [ax0cp,ax1cp]:
		plot_aesthetics(twin,fontsize=fontsize,fontweight=fontweight)

	plt.tight_layout()
	plt.subplots_adjust(hspace=0)

	if save_pref is not None:
		plt.savefig('figs/{}-int-shock-evo-fig0.png',format(save_pref))

	fig, ax = plt.subplots(2,2,sharex=True,figsize=(12,8))

	# Plot Arrival Time (ta) vs the energy fraction in synchrotron electron (asyn)
	plot_param_vs_time(is_emission,'ASYN', ax=ax[0,0], z=z, Tmin=Tmin, Tmax=Tmax,
		fontsize=fontsize, fontweight=fontweight, disp_xax=False, disp_yax=False,frame=frame)
	ax[0,0].set_ylabel(r'$\alpha_{syn}$',fontsize=fontsize,fontweight=fontweight)
	
	# Plot Arrival Time (ta) vs the dissipated energy (e)
	plot_param_vs_time(is_emission,'GAMMAE', ax=ax[0,1], y_factor=1/1e4,z=z, Tmin=Tmin, Tmax=Tmax,
		fontsize=fontsize, fontweight=fontweight, disp_xax=False, disp_yax=False,frame=frame)
	ax[0,1].set_ylabel(r'$\Gamma_{e}$/1e4',fontsize=fontsize,fontweight=fontweight)
	ax[0,1].yaxis.set_label_position("right")
	ax[0,1].yaxis.tick_right()

	# Plot Arrival Time (ta) vs the equipartition magnetic field (Beq)
	plot_param_vs_time(is_emission,'BEQ', ax=ax[1,0], z=z, Tmin=Tmin, Tmax=Tmax,
		fontsize=fontsize, fontweight=fontweight, disp_xax=False, disp_yax=False,marker='.',frame=frame)
	ax[1,0].set_yscale('log')
	ax[1,0].set_ylabel(r'B$_{eq}$',fontsize=fontsize,fontweight=fontweight)
	if(frame == "obs"):
		ax[1,0].set_xlabel(r't$_{obs}$ (sec)',fontsize=fontsize,fontweight=fontweight)
	if(frame == "source"):
		ax[1,0].set_xlabel(r't$_{e} (sec)$',fontsize=fontsize,fontweight=fontweight)

	# Plot Arrival Time (ta) vs the synchrotron energy (Esyn)
	plot_param_vs_time(is_emission,'ESYN', ax=ax[1,1], z=z, Tmin=Tmin, Tmax=Tmax,
		fontsize=fontsize, fontweight=fontweight, disp_xax=False, disp_yax=False,frame=frame)
	ax[1,1].set_yscale('log')
	ax[1,1].set_ylabel(r'$E_{syn}$/1e3',fontsize=fontsize,fontweight=fontweight)
	if(frame == "obs"):
		ax[1,1].set_xlabel(r't$_{obs}$ (sec)',fontsize=fontsize,fontweight=fontweight)
	if(frame == "source"):
		ax[1,1].set_xlabel(r't$_{e} (sec)$',fontsize=fontsize,fontweight=fontweight)
	ax[1,1].yaxis.set_label_position("right")
	ax[1,1].yaxis.tick_right()

	for i in range(2):
		for j in range(2):
			plot_aesthetics(ax[i,j],fontsize=fontsize,fontweight=fontweight)

	plt.tight_layout()
	plt.subplots_adjust(wspace=0,hspace=0)

	ax[0,0].set_xlim(-1)
	ax[0,0].set_ylim(-0.05,1.05)
	ax[0,1].set_ylim(-0.2,4.2)
	ax[1,0].set_ylim(0.5,2*10**6)
	ax[1,1].set_ylim(0.5,2*10**6)

	ax[0,0].grid(axis='x')
	ax[0,1].grid(axis='x')
	ax[1,0].grid(axis='x')
	ax[1,1].grid(axis='x')

	if save_pref is not None:
		plt.savefig('figs/{}-int-shock-evo-fig1.png'.format(save_pref))

##############################################################################################################################

def make_together_plots(shock_data, ax0, ax1,frame="obs", z=0, label=None, Tmin=None, Tmax=None,fontsize=14,fontweight='bold',guidelines=False,save_pref=None,color="C1",marker=".",markersize=7):
	"""
	Plot making method called by plot_together()

	Attributes:
	shock_data = the emission data to be plotted
	ax0 = first axis instance
	ax1 = second axis instance
	frame = string, should be given as "obs" or "source"
		"obs" indicates that the observed time will be used 
		"source" indicate that the emitted time will be used

	z = redshift to shift the light curve to

	label = optional label for the plotted light curve
	
	Tmin, Tmax = indicates the minimum and maximum time range to plot. If None is supplied, the minimum and maximum times of the supplied data files are used

	save_pref = if not left as None, the plot will be saved and the file name will have this prefix
	fontsize, fontweight = fontsize and fontweight of the plot font and labels on the plot
	
	guidelines = boolean, whether or not to include guidelines for the afterglow behavior (indicating whether a wind or constant medium )

	color = color of the data
	marker = marker of the data
	markersize = markersize of the data marker
	"""

	### First Plot ###

	# T_a vs B_eq
	plot_param_vs_time(shock_data,'BEQ', ax=ax0[0,0], z=z, Tmin=Tmin, Tmax=Tmax,
			fontsize=fontsize, fontweight=fontweight, disp_xax=False, disp_yax=False, marker=marker,color=color,label=label,frame=frame,markersize=markersize)

	# T_a vs Gamma_r
	if guidelines == True:
		rhowindline = lambda t, t0, norm: norm*np.power(t/t0,-1./4.)
		rhoconstline = lambda t, t0, norm: norm*np.power(t/t0,-3./8.)

		tstart = 1e2
		tstop = 1e8
		tnum = 1e2
		g_norm_wind = rhowindline(tstart,shock_data['TA'][np.argmax(shock_data['TA']>tstart)],shock_data['GAMMAR'][np.argmax(shock_data['TA']>tstart)])
		g_norm_const = rhoconstline(tstart,shock_data['TA'][np.argmax(shock_data['TA']>tstart)],shock_data['GAMMAR'][np.argmax(shock_data['TA']>tstart)])
		t = np.linspace(tstart,tstop,num=int(tnum))	
		ax0[0,1].plot(t,rhowindline(t,tstart,g_norm_wind),label=r"$t^{-1/4}$",color='r')
		ax0[0,1].plot(t,rhoconstline(t,tstart,g_norm_const),label=r"$t^{-3/8}$",color='k')

	plot_param_vs_time(shock_data,'GAMMAR', ax=ax0[0,1], z=z, Tmin=Tmin, Tmax=Tmax,
			fontsize=fontsize, fontweight=fontweight, disp_xax=False, disp_yax=False, marker=marker,color=color,frame=frame,markersize=markersize)

	# T_a vs e_diss
	plot_param_vs_time(shock_data,'EDISS', ax=ax0[1,0], z=z, Tmin=Tmin, Tmax=Tmax,
			fontsize=fontsize, fontweight=fontweight, disp_xax=False, disp_yax=False, marker=marker,color=color,frame=frame,markersize=markersize)

	# T_a vs E_syn
	plot_param_vs_time(shock_data,'ESYN', ax=ax0[1,1], z=z, Tmin=Tmin, Tmax=Tmax,
			fontsize=fontsize, fontweight=fontweight, disp_xax=False, disp_yax=False, marker=marker,color=color,frame=frame,markersize=markersize)


	# Plot Aesthetics

	# Format Top Left plot, T_a vs B_eq
	ax0[0,0].set_ylabel(r"B$_{EQ}$",fontsize=fontsize,fontweight=fontweight)
	# ax0[0,0].set_xlabel(r"$t_a$",fontsize=fontsize,fontweight=fontweight)
	ax0[0,0].set_yscale("log")
	ax0[0,0].set_xscale("log")
	ax0[0,0].legend(fontsize=fontsize)

	# Format Top Right plot, T_a vs Gamma_r 
	ax0[0,1].set_ylabel(r"$\Gamma_r$",fontsize=fontsize,fontweight=fontweight)
	# ax0[0,1].set_xlabel(r"$t_a$",fontsize=fontsize,fontweight=fontweight)
	ax0[0,1].yaxis.set_label_position("right")
	ax0[0,1].yaxis.tick_right()
	ax0[0,1].set_yscale("log")
	ax0[0,1].set_xscale("log")

	# Format Bottom Left plot, T_a vs E_diss
	ax0[1,0].set_ylabel(r"E$_{diss}$",fontsize=fontsize,fontweight=fontweight)
	if(frame == "obs"):
		ax0[1,0].set_xlabel(r't$_{obs}$ (sec)',fontsize=fontsize,fontweight=fontweight)
	if(frame == "source"):
		ax0[1,0].set_xlabel(r't$_{e} (sec)$',fontsize=fontsize,fontweight=fontweight)
	ax0[1,0].set_yscale("log")
	ax0[1,0].set_xscale("log")

	# Format Bottom Right plot, T_a vs E_synch
	ax0[1,1].set_ylabel(r"E$_{syn}$",fontsize=fontsize,fontweight=fontweight)
	if(frame == "obs"):
		ax0[1,1].set_xlabel(r't$_{obs}$ (sec)',fontsize=fontsize,fontweight=fontweight)
	if(frame == "source"):
		ax0[1,1].set_xlabel(r't$_{e} (sec)$',fontsize=fontsize,fontweight=fontweight)
	ax0[1,1].yaxis.set_label_position("right")
	ax0[1,1].yaxis.tick_right()
	ax0[1,1].set_yscale("log")
	ax0[1,1].set_xscale("log")

	# Make plots look good
	for i in range(2):
		for j in range(2):
			plot_aesthetics(ax0[i,j],fontsize=fontsize,fontweight=fontweight)

	plt.tight_layout()
	plt.subplots_adjust(wspace=0,hspace=0)

	if save_pref is not None:
		plt.savefig('figs/{}-all-shock-evo-fig0.png'.format(save_pref))

	### Second Plot ###

	# T_a vs T_e
	plot_param_vs_time(shock_data,'TE', ax=ax1[0], z=z, Tmin=Tmin, Tmax=Tmax,
			fontsize=fontsize, fontweight=fontweight, disp_xax=False, disp_yax=False, marker=marker,color=color, label=label,frame=frame,markersize=markersize)

	# T_a vs del T_a
	# Make a copy of the axis in order to over plot two separate data sets
	# ax1cp = ax1[0].twinx()
	# plot_param_vs_time(shock_data,'DELT', ax=ax1cp, z=z,Tmin=Tmin, Tmax=Tmax,
	# 	fontsize=fontsize, fontweight=fontweight, disp_xax=False, disp_yax=False,marker=marker,color=color,frame=frame)


	# T_a vs Gamma_e
	plot_param_vs_time(shock_data,'GAMMAE', ax=ax1[1], z=z, Tmin=Tmin, Tmax=Tmax,
			fontsize=fontsize, fontweight=fontweight, marker=marker,color=color,frame=frame,markersize=markersize)

	# Plot Aesthetics
	# Format Top plot, T_a vs T_e
	
	ax1[0].set_ylabel(r"$t_e$",fontsize=fontsize,fontweight=fontweight)
	ax1[0].set_xlabel(r"$t_a$",fontsize=fontsize,fontweight=fontweight)

	# ax1cp.set_ylabel(r'$\Delta t$',fontsize=fontsize,fontweight=fontweight)
	# ax1cp.yaxis.set_label_position("right")
	# ax1cp.yaxis.tick_right()

	ax1[0].set_yscale("log")
	ax1[0].set_xscale("log")
	# ax1cp.set_yscale("log")
	# ax1cp.set_xscale("log")
	ax1[0].legend(fontsize=fontsize)

	# Format Bottom plot, T_a vs Gamma_e
	ax1[1].set_ylabel(r"$\Gamma_{e}$",fontsize=fontsize,fontweight=fontweight)
	if(frame == "obs"):
		ax1[1].set_xlabel(r't$_{obs}$ (sec)',fontsize=fontsize,fontweight=fontweight)
	if(frame == "source"):
		ax1[1].set_xlabel(r't$_{e}$ (sec)',fontsize=fontsize,fontweight=fontweight)
	ax1[1].set_yscale("log")
	ax1[1].set_xscale("log")

	# Make plots look good
	for i in range(2):
		plot_aesthetics(ax1[i],fontsize=fontsize,fontweight=fontweight)
	# plot_aesthetics(ax1cp,fontsize=fontsize,fontweight=fontweight)


	plt.tight_layout()
	plt.subplots_adjust(hspace=0)

	if save_pref is not None:
		plt.savefig('figs/{}-all-shock-evo-fig1.png'.format(save_pref))

##############################################################################################################################

def plot_together(is_data = None,fs_data=None, rs_data=None,frame="obs", z=0, Tmin=None, Tmax=None,save_pref=None,fontsize=14,fontweight='bold',markregime=True,markersize=10,guidelines=False):
	"""
	Make diagnostics plots for the instantaneous jet dynamics parameters. This will create six plots. All shock emission data provided will be included within these six plots.

	Attributes:
	is_data = the internal emission data to be plotted
	fs_data = the forward shock emission data to be plotted
	rs_data = the reverse shock emission data to be plotted

	frame = string, should be given as "obs" or "source"
		"obs" indicates that the observed time will be used 
		"source" indicate that the emitted time will be used

	z = redshift to shift the light curve to
	
	Tmin, Tmax = indicates the minimum and maximum time range to plot. If None is supplied, the minimum and maximum times of the supplied data files are used

	save_pref = if not left as None, the plot will be saved and the file name will have this prefix
	fontsize, fontweight = fontsize and fontweight of the plot font and labels on the plot
	
	markregime = boolean, indicates whether fast and slow cooling regimes should be indicated on the plot by different markers
	markersize = markersize of the data marker
	"""


	fig0, ax0 = plt.subplots(2,2,sharex=True,figsize=(12,8))
	fig1, ax1 = plt.subplots(2,1,sharex=True,figsize=(6,6))

	annot0 = []
	annot0.append( ax0[0,0].annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points", bbox=dict(boxstyle="round", fc="w"),arrowprops=dict(arrowstyle="->")) )
	annot0.append( ax0[0,1].annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points", bbox=dict(boxstyle="round", fc="w"),arrowprops=dict(arrowstyle="->")) )
	annot0.append( ax0[1,0].annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points", bbox=dict(boxstyle="round", fc="w"),arrowprops=dict(arrowstyle="->")) )
	annot0.append( ax0[1,1].annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points", bbox=dict(boxstyle="round", fc="w"),arrowprops=dict(arrowstyle="->")) )
	
	annot1 = []
	annot1.append( ax1[0].annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points", bbox=dict(boxstyle="round", fc="w"),arrowprops=dict(arrowstyle="->")) )
	annot1.append( ax1[1].annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points", bbox=dict(boxstyle="round", fc="w"),arrowprops=dict(arrowstyle="->")) )

	data_holder = []

	def onpick3(event, fig, ax, data_holder):

		artist = event.artist
		for i in range( len(ax.get_children() ) ):
			if(ax.get_children()[i] == artist ):
				
				facecolor = ax.get_children()[i].get_facecolor()

				# This is a list of indices for each point located underneath of the mouse click
				ind_list = event.ind
				# Take central one in the list  
				ind = ind_list[int(len(ind_list)/2)]

				# For fig 0
				for j in range(2):
					for k in range(2):
						# For fig 1submit_time
						# Access the selected data point position 
						d = ax0[j,k].collections[i]
						pos = d.get_offsets()[ind]

						# Set the position of the annotation 
						annot0[k+(j*2)].xy = pos

						# Display the point index
						text = "SH. IND. = {}".format(data_holder[i]["SHIND"][ind])
						annot0[k+(j*2)].set_text(text)

						# Set color and alpha of text box for clarity
						annot0[k+(j*2)].get_bbox_patch().set_facecolor(facecolor)
						annot0[k+(j*2)].get_bbox_patch().set_alpha(0.4)

						# Redraw all axes to update text box position and information
						ax0[j,k].redraw_in_frame()

				# For fig 1
				for j in range(2):
					# For fig 1
					# Access the selected data point position 
					d = ax1[j].collections[i]
					pos = d.get_offsets()[ind]

					# Set the position of the annotation 
					annot1[j].xy = pos

					# Display the point index
					text = "SH. IND. = {}".format(data_holder[i]["SHIND"][ind])
					annot1[j].set_text(text)

					# Set color and alpha of text box for clarity
					annot1[j].get_bbox_patch().set_facecolor(facecolor)
					annot1[j].get_bbox_patch().set_alpha(0.4)

					# Redraw all axes to update text box position and information
					ax1[j].redraw_in_frame()

			# Redraw all figures to update text box position and information
			fig0.canvas.draw_idle()
			fig1.canvas.draw_idle()



	if is_data is not None:
		if (markregime == True):
			fastcool_data = is_data[is_data['NUM']>is_data['NUC']]
			if len(fastcool_data) > 0:
				make_together_plots(shock_data=fastcool_data,label="IS - FC", color="C0", ax0=ax0, ax1=ax1, z=z, Tmin=Tmin, Tmax=Tmax, fontsize=fontsize,fontweight=fontweight,frame=frame,markersize=markersize)
			data_holder.append(fastcool_data)

			slowcool_data = is_data[is_data['NUM']<=is_data['NUC']]
			if len(slowcool_data) > 0:
				make_together_plots(shock_data=slowcool_data,label="IS - SC", color="C0", marker='x', ax0=ax0, ax1=ax1, z=z, Tmin=Tmin, Tmax=Tmax, fontsize=fontsize,fontweight=fontweight,frame=frame,markersize=markersize)
			data_holder.append(slowcool_data)

		else:
			make_together_plots(shock_data=is_data,label="IS", color="C0", ax0=ax0, ax1=ax1, z=z, Tmin=Tmin, Tmax=Tmax, fontsize=fontsize,fontweight=fontweight,frame=frame,markersize=markersize)
			data_holder.append(is_data)

	if fs_data is not None:
		if (markregime == True):
			fastcool_data = fs_data[fs_data['NUM']>fs_data['NUC']]
			if len(fastcool_data) > 0:
				make_together_plots(shock_data=fastcool_data,label="FS - FC", color="C1", ax0=ax0, ax1=ax1, z=z, Tmin=Tmin, Tmax=Tmax, fontsize=fontsize,fontweight=fontweight,frame=frame,markersize=markersize,guidelines=guidelines)
			data_holder.append(fastcool_data)
			
			slowcool_data = fs_data[fs_data['NUM']<=fs_data['NUC']]
			if len(slowcool_data) > 0:
				make_together_plots(shock_data=slowcool_data,label="FS - SC", color="C1", marker='x', ax0=ax0, ax1=ax1, z=z, Tmin=Tmin, Tmax=Tmax, fontsize=fontsize,fontweight=fontweight,frame=frame,markersize=markersize,guidelines=guidelines)
			data_holder.append(slowcool_data)

		else:
			make_together_plots(shock_data=fs_data,label="FS", color="C1", ax0=ax0, ax1=ax1, z=z, Tmin=Tmin, Tmax=Tmax, fontsize=fontsize,fontweight=fontweight,frame=frame,markersize=markersize,guidelines=guidelines)
			data_holder.append(fs_data)

	if rs_data is not None:
		if (markregime == True):
			fastcool_data = rs_data[rs_data['NUM']>rs_data['NUC']]
			if len(fastcool_data) > 0:
				make_together_plots(shock_data=fastcool_data,label="RS - FC", color="C2", ax0=ax0, ax1=ax1, z=z, Tmin=Tmin, Tmax=Tmax, fontsize=fontsize,fontweight=fontweight,frame=frame,markersize=markersize)
			data_holder.append(fastcool_data)

			slowcool_data = rs_data[rs_data['NUM']<=rs_data['NUC']]
			if len(slowcool_data) > 0:
				make_together_plots(shock_data=slowcool_data,label="RS - SC", color="C2", marker='x', ax0=ax0, ax1=ax1, z=z, Tmin=Tmin, Tmax=Tmax, fontsize=fontsize,fontweight=fontweight,frame=frame,markersize=markersize)
			data_holder.append(slowcool_data)

		else:
			make_together_plots(shock_data=rs_data,label="RS", color="C2", ax0=ax0, ax1=ax1, z=z, Tmin=Tmin, Tmax=Tmax, fontsize=fontsize,fontweight=fontweight,frame=frame,markersize=markersize)
			data_holder.append(rs_data)


	fig0.canvas.mpl_connect("pick_event", lambda event: onpick3(event, fig0, ax0[0,0],data_holder))
	fig0.canvas.mpl_connect("pick_event", lambda event: onpick3(event, fig0, ax0[0,1],data_holder))
	fig0.canvas.mpl_connect("pick_event", lambda event: onpick3(event, fig0, ax0[1,0],data_holder))
	fig0.canvas.mpl_connect("pick_event", lambda event: onpick3(event, fig0, ax0[1,1],data_holder))

	fig1.canvas.mpl_connect('pick_event', lambda event: onpick3(event, fig1, ax1[0],data_holder))
	fig1.canvas.mpl_connect('pick_event', lambda event: onpick3(event, fig1, ax1[1],data_holder))


	if save_pref is not None:
		fig0.savefig('figs/{}-all-shock-evo-fig0.png'.format(save_pref))
		fig1.savefig('figs/{}-all-shock-evo-fig1.png'.format(save_pref))

	return fig0, fig1

##############################################################################################################################

def plot_observables(is_emission,th_emission,frame="obs",ax=None,z=0, save_pref=None,fontsize=14,fontweight='bold'):
	"""
	Plot observables

	This isn't done yet, so don't pay attention to it
	"""

	if ax is None:
		fig, ax = plt.subplots(2,2,figsize=(8,8))

	# Epeak vs Time of the non-thermal component
	plot_param_vs_time(is_emission, "ESYN", ax=ax[0,0], z=z, fontsize=fontsize, fontweight=fontweight, frame=frame)

	if(frame == "obs"):
		ax[0,0].set_xlabel(r't$_{obs}$ (sec)',fontsize=fontsize,fontweight=fontweight)
	if(frame == "source"):
		ax[0,0].set_xlabel(r't$_{e}$ (sec)',fontsize=fontsize,fontweight=fontweight)
	ax[0,0].set_ylabel(r"E$_{peak}$ (keV)",fontsize=fontsize,fontweight=fontweight)

	# Flux vs Epeak of the non-thermal component
	ax[0,1].scatter(x=is_emission['ESYN'],y=is_emission['EDISS'],marker=".")

	ax[0,1].set_yscale('log')
	ax[0,1].set_xscale('log')

	ax[0,1].set_xlabel(r"E$_{peak}$ (keV)",fontsize=fontsize,fontweight=fontweight)
	ax[0,1].set_ylabel(r'F (erg/s)',fontsize=fontsize,fontweight=fontweight)
	
	# alpha (low energy power law index) vs Time of the non-thermal component



	# Flux vs Temperature of the thermal component
	ax[1,1].scatter(x=th_emission['TEMP']*kb_kev,y=th_emission['FLUX'],marker=".")

	ax[1,1].set_xlabel(r"k$_B$T (keV)",fontsize=fontsize,fontweight=fontweight)
	ax[1,1].set_ylabel(r'F (erg/s)',fontsize=fontsize,fontweight=fontweight)

	# Make plots look good
	for i in range(2):
		for j in range(2):
			plot_aesthetics(ax[i,j],fontsize=fontsize,fontweight=fontweight)
			ax[i,j].grid()

	plt.tight_layout()

	if save_pref is not None:
		plt.savefig('figs/{}-observables.png'.format(save_pref))

##############################################################################################################################

def plot_synch_cooling_regime(emission,frame="obs",ax=None,z=0,label=None, color="C0", markers=[".","^"], markersize=None, alpha=1, save_pref=None, Tmin=None, Tmax=None, fontsize=14,fontweight='bold',ylogscale=True,xlogscale=True):
	"""
	Plot nu_c and nu_m vs time

	Attributes:
	is_data = the internal emission data to be plotted
	fs_data = the forward shock emission data to be plotted
	rs_data = the reverse shock emission data to be plotted

	frame = string, should be given as "obs" or "source"
		"obs" indicates that the observed time will be used 
		"source" indicate that the emitted time will be used

	ax = axis to plot the data on

	z = redshift to shift the light curve to
	
	label = optional label for the plotted light curve

	color = color of the data
	marker = marker of the data
	markersize = markersize of the data marker
	alpha = transparency of the data points 

	Tmin, Tmax = indicates the minimum and maximum time range to plot. If None is supplied, the minimum and maximum times of the supplied data files are used

	save_pref = if not left as None, the plot will be saved and the file name will have this prefix
	fontsize, fontweight = fontsize and fontweight of the plot font and labels on the plot
	"""

	time_str = "TA"
	if(frame=="source"):
		time_str = "TE"

	if Tmin is None:
		Tmin = emission[time_str][0]
	if Tmax is None:
		Tmax = emission[time_str][-1]

	y_factor = planck_kev*emission['GAMMAR'][(emission[time_str]>Tmin) & (emission[time_str] < Tmax)]

	# Make plot instance if it doesn't exist
	if ax is None:
		ax = plt.figure(figsize=(10,8)).gca()

	# Plot temperature of the thermal component vs time (in observer frame)
	plot_param_vs_time(emission,'NUC', ax=ax, z=z, y_factor=y_factor,Tmin=Tmin, Tmax=Tmax, marker=markers[0],
		markersize=markersize, color=color, label=label, fontsize=fontsize, fontweight=fontweight,frame=frame,alpha=alpha)
	plot_param_vs_time(emission,'NUM', ax=ax, z=z, y_factor=y_factor,Tmin=Tmin, Tmax=Tmax, marker=markers[1],
		markersize=markersize, color=color, fontsize=fontsize, fontweight=fontweight,frame=frame,alpha=alpha)

	ax.set_xlabel(r't$_{obs}$',fontsize=fontsize,fontweight=fontweight)
	ax.set_ylabel(r'E (KeV)',fontsize=fontsize,fontweight=fontweight)
	ax.set_title(r"$\nu_c$ = {}, $\nu_m$ = {}".format(repr(markers[0]),repr(markers[1])),fontsize=fontsize,fontweight=fontweight)
	ax.set_yscale('log')


	# Make plots look good
	plot_aesthetics(ax,fontsize=fontsize,fontweight=fontweight)

	if(ylogscale == True):
		ax.set_yscale('log')
	if(xlogscale == True):
		ax.set_xscale('log')

	if label is not None:
		ax.legend(fontsize=fontsize)

	ax.grid(True)
	plt.tight_layout()

	if save_pref is not None:
		plt.savefig('figs/{}-synch-cooling-regime.png'.format(save_pref))


##############################################################################################################################

def lum_dis(z: float):
	""" 
	Caclulate luminosity distance for a given redshift z
	"""
	if(z == 0):
		return 1
	else:
		# bol_lum = [1,100000] # bolumetric luminosity range
		c = 3*np.power(10,10) # speed of light, cm/s
		omega_m = 0.3 # matter density of the universe
		omega_lam = 0.7 # dark energy density of the universe
		H0 = 67.4*np.power(10,5) # Hubbles Constant cm/s/Mpc

		lum_dis_Mpc = ((1+z)*c/(H0) ) * integrate.quad(lambda zi: 1/np.sqrt( ((omega_m*np.power(1+zi,3) )+omega_lam) ),0,z)[0]
		lum_dis_cm = lum_dis_Mpc * 3.086e24 # Mpc -> cm
		return lum_dis_cm

##############################################################################################################################


if __name__ == '__main__':

	z = 0


	# save_pref = "2022-08-17/2022-08-17"

	"""
	Shell Lorentz Distribution
	"""
	
	fig = plt.figure()
	ax = fig.gca()
	plot_lor_dist_simple('data-file-dir/synthGRB_shell_dist.txt',joined=True,ax=ax,fig=fig,title=None)
	# plot_lor_dist_simple('data-file-dir/synthGRB_shell_dist.txt',joined=True,ax=ax,fig=fig,color="C1",title=None)
	# ax.invert_xaxis()
	
	# plot_lor_dist('data-file-dir/synthGRB_shell_dist.txt',show_zoomed=False)
	# ani = plot_lor_dist_anim('data-file-dir/synthGRB_shell_dist.txt')

	"""
	Synthetic spectrum 
	"""

	ax_spec = plt.figure().gca()

	# Synthetic spectra with each component
	# plot_spec("data-file-dir/synthGRB_spec_IS.txt",ax=ax_spec,z=z,label="IS",color="C0",joined=True)
	# plot_spec("data-file-dir/synthGRB_spec_FS.txt",ax=ax_spec,z=z,label="FS",color="C1",joined=True)
	# plot_spec("data-file-dir/synthGRB_spec_RS.txt",ax=ax_spec,z=z,label="RS",color="C2",joined=True)
	# plot_spec("data-file-dir/synthGRB_spec_TH.txt",ax=ax_spec,z=z,label="TH",color="r",joined=True)
	# plot_spec("data-file-dir/synthGRB_spec_total.txt",ax=ax_spec,z=z,label="Tot",color="k",joined=True)

	# plot_spec("data-file-dir/synthGRB_spectrum_afterglow_opt_zoom_rs_xi-4.txt",ax=ax_spec,z=z,label=r"RS $\xi$ = 10$^{-4}$",color="hotpink",joined=True,alpha=0.7)
	# plot_spec("data-file-dir/synthGRB_spectrum_afterglow_opt_zoom_rs_xi-3.txt",ax=ax_spec,z=z,label=r"RS $\xi$ = 10$^{-3}$",color="C2",joined=True,alpha=1)
	# plot_spec("data-file-dir/synthGRB_spectrum_afterglow_opt_zoom_rs_xi-2.txt",ax=ax_spec,z=z,label=r"RS $\xi$ = 10$^{-2}$",color="C0",joined=True,alpha=0.7)
	# plot_spec("data-file-dir/synthGRB_spectrum_afterglow_opt_zoom_rs_xi-1.txt",ax=ax_spec,z=z,label=r"RS $\xi$ = 10$^{-1}$",color="purple",joined=True,alpha=0.7)
	# ax_spec.vlines(x=0.75, ymin=1.e39,ymax=1.e44,color="k",alpha=0.6,linestyle="dotted")

	# ax_spec.set_xlim(10**(-6),10**(3))
	# ax_spec.set_ylim(1.e39,1.e44)


	# add_FermiGBM_band(ax_spec)
	# plot_spec("data-file-dir/synthGRB_spec_total.txt",ax=ax_spec,z=z,label="Total",color="k")

	## Synthetic spectrum before convolusion
	# plot_spec("data-file-dir/spec_source.txt",ax=ax_spec,unc=False,label="Source")
	# plot_spec("data-file-dir/spec_source_fluc.txt",ax=ax_spec,unc=True,label="Pre-Conv")
	# plot_spec("data-file-dir/spec_model.txt",ax=ax_spec,unc=False,label="Model",joined=True)
	
	## Synthetic spectrum after convolusion
	# plot_spec("data-file-dir/spec_obs.txt",ax=ax_spec,unc=True,label="Obs")
	# plot_spec("data-file-dir/spec_model_conv.txt",ax=ax_spec,unc=False,label="Model",joined=True)
	# plot_spec("data-file-dir/spec_mod_emp.txt",ax=ax_spec,unc=False,label="Model",joined=True)

	# add_FermiGBM_band(ax_spec)
	# add_SwiftBAT_band(ax_spec)

	# ax_spec.set_xlim(0.1,1e5)
	# ax_spec.set_ylim(1e48,1e52)
	
	

	"""
	Synthetic light curve
	"""	
	# fig = plt.figure()
	# ax_lc = fig.gca()
	# plot_light_curve("data-file-dir/synthGRB_light_curve.txt",ax=ax_lc,fig=fig,z=z,label="Total",logscale=False,color="k",alpha=0.5)
	# plot_light_curve("data-file-dir/synthGRB_light_curve_TH.txt",ax=ax_lc, fig=fig,z=z,label="TH",color="r")
	# plot_light_curve("data-file-dir/synthGRB_light_curve_IS.txt",ax=ax_lc, fig=fig,z=z,label="IS",color="C0")
	# plot_light_curve("data-file-dir/synthGRB_light_curve_FS.txt",ax=ax_lc, fig=fig,z=z,label="FS",color="C1")
	# plot_light_curve("data-file-dir/synthGRB_light_curve_RS.txt",ax=ax_lc, fig=fig,z=z,label="RS",color="C2")

	# Interactive light curve
	# tbox = plot_light_curve_interactive(init_Tmin = 0, init_Tmax = 13, init_dT=0.2, init_Emin = 8, init_Emax = 40000,z=z,label="Total",with_comps=True)

	# Afterglow light curve
	# ax_afg_lc = plt.figure().gca()
	# plot_light_curve("data-file-dir/synthGRB_light_curve.txt",ax=ax_afg_lc,z=z,label="Prompt: Fermi-GBM",logscale=True,color="k")
	# plot_light_curve("data-file-dir/synthGRB_light_curve_afterglow_gbm.txt",ax=ax_afg_lc,z=z,label="AG: Fermi-GBM",logscale=True,color="C0")
	# plot_light_curve("data-file-dir/synthGRB_light_curve_afterglow_xrt.txt",ax=ax_afg_lc, fig = fig, z=z,label="AG: XRT",logscale=True,color="C4")
	# plot_light_curve("data-file-dir/synthGRB_light_curve_afterglow_opt.txt",ax=ax_afg_lc, fig = fig, z=z,label="AG: OPT, (1e-3, 5e-3) keV",logscale=True,color="C1")
	# ax_afg_lc.set_ylim(1e43,1e49)
	# ax_afg_lc.set_xlim(0.1)

	fig = plt.figure()
	ax_afg_lc = fig.gca()
	plot_light_curve("data-file-dir/synthGRB_light_curve_afterglow_opt_zoom_tot.txt",ax=ax_afg_lc, fig=fig ,z=z,label="AG: OPT, (1e-3, 5e-3) keV",logscale=True,color="k",xax_units="s")
	plot_light_curve("data-file-dir/synthGRB_light_curve_afterglow_opt_zoom_fs.txt",ax=ax_afg_lc, fig=fig ,z=z,label="FS",logscale=True,color="C1",xax_units="s")
	# plot_light_curve("data-file-dir/synthGRB_light_curve_afterglow_opt_zoom_rs.txt",ax=ax_afg_lc, fig=fig ,z=z,label="RS",logscale=True,color="C2",xax_units="s")

	# plot_light_curve("data-file-dir/synthGRB_light_curve_afterglow_opt_zoom_rs_xi-4.txt",ax=ax_afg_lc, fig=fig ,z=z,label=r"RS $\xi$ = 10$^{-4}$",logscale=True,color="hotpink",xax_units="s",alpha=0.3)
	plot_light_curve("data-file-dir/synthGRB_light_curve_afterglow_opt_zoom_rs_xi-3.txt",ax=ax_afg_lc, fig=fig ,z=z,label=r"RS $\xi$ = 10$^{-3}$",logscale=True,color="C2",xax_units="s")
	# plot_light_curve("data-file-dir/synthGRB_light_curve_afterglow_opt_zoom_rs_xi-2.txt",ax=ax_afg_lc, fig=fig ,z=z,label=r"RS $\xi$ = 10$^{-2}$",logscale=True,color="C0",xax_units="s",alpha=0.3)
	# plot_light_curve("data-file-dir/synthGRB_light_curve_afterglow_opt_zoom_rs_xi-1.txt",ax=ax_afg_lc, fig=fig ,z=z,label=r"RS $\xi$ = 10$^{-1}$",logscale=True,color="purple",xax_units="s",alpha=0.3)



	"""
	Jet dynamics plots 
	
	"""
	
	# therm_emission = load_therm_emission("data-file-dir/synthGRB_jet_params_TH.txt")
	# plot_evo_therm(therm_emission,xlogscale=False,z=1)
	
	# is_data = load_is_emission("data-file-dir/synthGRB_jet_params_IS.txt")
	# fs_data = load_fs_emission("data-file-dir/synthGRB_jet_params_FS.txt")
	# rs_data = load_rs_emission("data-file-dir/synthGRB_jet_params_RS.txt")

	# Plot everything together:
	# fig0, fig1 = plot_together(is_data=is_data,fs_data=fs_data,rs_data=rs_data)
	# fig0, fig1 = plot_together(fs_data=fs_data,rs_data=rs_data)
	# fig0, fig1 = plot_together(fs_data=fs_data,guidelines=True)

	
	# # Plot nu_c and nu_m: 
	# ax_synch_reg = plt.figure(figsize=(10,8)).gca()
	# markers = [".","^"]
	# plot_synch_cooling_regime(is_data,ax=ax_synch_reg,Tmin=0,Tmax=20,label="IS",color="C0",markers=markers,alpha=0.8,markersize=16)
	# plot_synch_cooling_regime(fs_data,ax=ax_synch_reg,label="FS",color="C1",markers=markers,alpha=0.6,markersize=16,frame="obs")
	# plot_synch_cooling_regime(rs_data,ax=ax_synch_reg,label="RS",color="C2",markers=markers,alpha=0.8,markersize=16,frame="obs")
	# add_FermiGBM_band(ax_synch_reg,axis="y")


	# ax = plt.figure().gca()
	# plot_param_vs_time(fs_data,'DELT', ax=ax, z=0,disp_xax=True, disp_yax=True,color="C1",frame="obs")
	# plot_param_vs_time(rs_data,'DELT', ax=ax, z=0,disp_xax=True, disp_yax=True,color="C2",frame="obs")
	# ax.set_yscale('log')
	# ax.set_xscale('log')

	# # Display Fermi/GBM - NAI energy band
	# ax_synch_reg.axhspan(ymin=1e-3,ymax=5e-3,xmin=0,xmax=1,alpha=0.4,facecolor='grey',label='Optical Band')
	

	"""
	Observables
	"""
	"""
	th_emission = load_therm_emission("data-file-dir/synthGRB_jet_params_therm.txt")
	is_emission = load_is_emission("data-file-dir/synthGRB_jet_params_is.txt")

	plot_observables(is_emission, th_emission)
	"""


	"""
	Testing
	"""
	# fs_data = load_fs_emission("data-file-dir/synthGRB_jet_params_FS.txt")
	# ax = plt.figure().gca()
	# plot_param_vs_time(fs_data,"THETA",frame="obs",ax=ax)
	# ax.set_xscale('log')


	plt.show()

