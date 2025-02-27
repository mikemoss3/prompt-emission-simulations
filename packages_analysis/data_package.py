import numpy as np
from asymmetric_uncertainty import a_u

# File used to define Data class

class Data(object):
	def __init__(self,file_name = None):
		if file_name is None:
			self.data=None
		else:
			self.load_data(file_name)

		self.light_curve = None # Currently loaded light curve
		self.spectrum = None # Currently loaded spectrum 
		self.spectra = np.zeros(shape=0,dtype=[("TSTART",float),("TEND",float),("SPECTRUM",tuple)]) # Time resolved spectrum array

	def load_spectrum(self,file_name,tstart=None,tend=None):

		if tstart is not None:
			# Check that both a start and stop time were given 
			if tend is None:
				print("Please provide both a start and end time (or neither).")
				return 0;

			# Load the spectrum designated by the file name
			
			tmp_data = np.genfromtxt(file_name,dtype=[("ENERGY",float),("RATE",float),("UNC",float)])

			loaded_spectrum = np.zeros(shape=len(tmp_data),dtype=[("ENERGY",float),("RATE",a_u)] )
			loaded_spectrum['ENERGY'] = tmp_data['ENERGY']
			loaded_spectrum['RATE'] = [a_u(tmp_data['RATE'][i], tmp_data['UNC'][i],tmp_data['UNC'][i]) for i in range(len(tmp_data))]
			
			# loaded_spectrum = np.genfromtxt(file_name,dtype=[("ENERGY",float),("RATE",float),("UNC",float)])

			# Check if this is the first loaded spectrum 
			if len(self.spectra) == 0:
				self.spectra = np.insert(self.spectra,0,(tstart,tend,loaded_spectrum))
				return 0;
			else:
				# If not, find the index where to insert this spectrum (according to the time)
				for i in range(len(self.spectra)):
					if self.spectra[i]['TSTART'] > tstart:
						# Insert the new spectrum 
						self.spectra = np.insert(self.spectra,i,(tstart,tend,loaded_spectrum))
						return 0;
					# If the new spectrum is the last to start, append it to the end
					self.spectra = np.insert(self.spectra,len(self.spectra),(tstart,tend,loaded_spectrum))
					return 0;
		else:
			self.spectrum = np.genfromtxt(file_name,dtype=[('ENERGY',float),('RATE',a_u)])
			return 0;

	def set_spectrum(self,spec_array,tstart=None,tend=None):

		# Check that the array is in the correct format
		if spec_array.dtype.names != ('ENERGY','RATE'):
			print("Please provide an array with three columns: ENERGY and RATE (both floats)")

		if tstart is not None:
			# Check that both a start and stop time were given 
			if tend is None:
				print("Please provide both a start and end time.")
				return 0;

			# Check if this is the first loaded spectrum 
			if len(self.spectra) == 0:
				self.spectra = np.insert(self.spectra,0,(tstart,tend,spec_array))
				return 0;
			else:
				# If not, find the index where to insert this spectrum (according to the time)
				for i in range(len(self.spectra)):
					if self.spectra[i]['TSTART'] > tstart:
						# Insert the new spectrum 
						self.spectra = np.insert(self.spectra,i,(tstart,tend,spec_array))
						return 0;
					# If the new spectrum is the last to start, append it to the end
					self.spectra = np.insert(self.spectra,len(self.spectra),(tstart,tend,spec_array))
					return 0;
		else:
			self.spectrum = spec_array
			return 0;

	def load_light_curve(self,file_name,inc_unc = False):
		
		if inc_unc is False:
			self.light_curve = np.genfromtxt(file_name,dtype=[('TIME',float),('RATE',float)])
		else:
			self.light_curve = np.genfromtxt(file_name,dtype=[('TIME',float),('RATE',float),('UNC',float)])


