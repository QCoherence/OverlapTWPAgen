import numpy as np

import scipy.constants as cst
import scipy.optimize as optimization

# import ipynbname
import os
import json


class LER_parameters:

	def __init__(self, fab_parameters, device_parameters):

		self.module = 'LER_parameters'
		self.version = '1.0.0'

		self.epsilon0 = cst.epsilon_0

		self.c_c = fab_parameters['capacitor_parameters']['capacitance_per_unit_area']*1e-3 #F/m^2
		self.N_capa = device_parameters['capacitor_parameters']['number_of_capacitors']
		self.C = np.asarray(device_parameters['capacitor_parameters']['capacitance_value'])*1e-15 #F
		self.coupling_length = 2*device_parameters['meander_parameters']['length_of_coupling_step']
		self.l_meander = device_parameters['meander_parameters']['length_of_meander']
		self.coupling_distance = device_parameters['resonator_parameters']['coupling_distance']
		self.fr = device_parameters['resonator_parameters']['resonant_frequency'] # GHz

	def get_params(self, **kwargs):

		if 'print_params' in kwargs:
			print_params = kwargs.get("print_params")
		else:
			print_params = False

		### Capacitor dimensions
		A_capa = self.N_capa*self.C/self.c_c

		if print_params:
			print('Capacitor capacitance per unit area: c = %.2f fF/um^2' %(self.c_c*1e3))
			print('Number of capacitors: N_capa = %.f' %(self.N_capa))
			print('Meander length: l_meander = %.2f mm' %(self.l_meander*1e-3))
			print('Coupling length: l_coupling = %.f um' %(self.coupling_length))
			print('fr (GHz) | C (fF) | A (um^2) | coupling (um)')
			for i in range(len(self.C)):
				print('%.2f \t | %.f \t | %.2f \t | %.f' %(self.fr[i], self.C[i]*1e15, A_capa[i]*1e12, self.coupling_distance[i]))

		return A_capa*1e12



class LH_parameters:

	def __init__(self, fab_parameters, device_parameters):

		self.module = 'LH_parameters'
		self.version = '1.0.0'

		self.Z0 = 50
		self.epsilon0 = cst.epsilon_0
		self.k_b = cst.k #J/K
		self.e = cst.e #C
		self.hbar = cst.hbar #J*s
		self.h = cst.h #J*s
		self.phi0 = self.hbar/(2*self.e) #Wb
		self.Delta0 = 210.*1e-6 #V

		self.buisson_factor = fab_parameters['junction_parameters']['buisson_factor']
		self.heating_factor = fab_parameters['junction_parameters']['heating_factor']

		self.c_j = fab_parameters['junction_parameters']['capacitance_per_unit_area']*1e-3 #F/m^2
		self.j_c = fab_parameters['junction_parameters']['critical_current_density']*1e4 #A/m^2

		self.c_c = fab_parameters['capacitor_parameters']['capacitance_per_unit_area']*1e-3 #F/m^2

		self.Wj = device_parameters['junction_parameters']['width_of_junction']*1e-6 #m
		self.Hj = device_parameters['junction_parameters']['height_of_junction']*1e-6 #m

		self.Ncapa = device_parameters['capacitor_parameters']['number_of_capacitors_per_unit_cell']
		self.Ncell = device_parameters['TWPA_parameters']['number_of_cells']

		self.f0 = device_parameters['TWPA_parameters']['low_cutoff_frequency']*1e9 #Hz

		self.frequency_scale = 1e9


	def get_params(self, **kwargs):

		if 'print_params' in kwargs:
			print_params = kwargs.get("print_params")
		else:
			print_params = False

		### Target inductance to ground
		L_target = self.Z0/(2*np.pi*self.f0)

		### Junction area
		Aj = self.Wj*self.Hj

		### Junction resistance at room temperature
		Rj = np.pi*self.Delta0/(2*Aj*self.j_c*self.buisson_factor)

		### Critical current
		Ic = Aj*self.j_c/self.heating_factor

		### Junction normal state resistance
		Rn = np.pi*self.Delta0/(2*Ic)

		### Josephson Capacitance
		Cj = Aj*self.c_j

		### Josephson Inductance
		Lj = (self.phi0/Ic)

		### Number of junctions per unit cell
		Nj_ground = round(L_target/Lj)
		if Nj_ground%2 != 0:
			Nj_ground += 1

		### Inductance of the jj array to ground
		Lj_ground = Nj_ground*Lj
		### Capacitance of the jj array to ground
		Cj_ground = Cj/Nj_ground

		### Series capacitance
		C =Lj_ground/(self.Z0**2)

		### Capacitor dimensions
		A_capa = self.Ncapa*C/self.c_c
		# A_capa = self.N_capa*C*self.t_AlOx/(self.epsilon0*self.epsilon_AlOx)

		### Junction plasma frequency
		fj = 1/(2*np.pi*np.sqrt(Lj*Cj))

		### Low cutoff frequency
		f0 = 1/(2*np.pi*np.sqrt(Lj_ground*C))

		if print_params:
			print('\033[1m Parameters \033[0m')
			print('Junction capacitance per unit area: c_j = %.2f fF/um^2' %(self.c_j*1e3))
			print('Junction critical current density: j_c = %.2f A/cm^2' %(self.j_c*1e-4))
			print('Capacitor capacitance per unit area: c_c = %.2f fF/um^2' %(self.c_c*1e3))
			print('Number of cells: Ncell = %.f' %(self.Ncell))
			print('Number of junctions to ground: Nj_ground = %.f' %(Nj_ground))
			print('Number of capacitors per cell: Ncapa = %.f' %(self.Ncapa))
			print('Junction dimensions: H = %.2f um | W = %.2f um | A = %.2f um^2' %(self.Hj*1e6, self.Wj*1e6, Aj*1e12))
			print('Room temp resistance: Rj = %.2f Ohm' %(Rj))
			print('Critical current: Ic = %.2f uA' %(Ic*1e6))
			print('Normal state resistance: Rn = %.2f Ohm' %(Rn))
			print('Josephson inductance: Lj = %.2f pH' %(Lj*1e12))
			print('Josephson capacitance: Cj = %.2f fF' %(Cj*1e15))
			print('Inductance to ground: Lj_ground = %.2f nH' %(Lj_ground*1e9))
			print('Capacitance to ground: Cj_ground = %.2f fF' %(Cj_ground*1e15))
			print('Series capacitance: C = %.2f fF' %(C*1e15))
			print('Capacitor area: A = %.2f um^2' %(A_capa*1e12))
			print ('Plasma frequency: fj = %.2f GHz' %(fj/self.frequency_scale))
			print ('Cut-off frequency: f0 = %.2f GHz' %(f0/self.frequency_scale))

		return Nj_ground, A_capa*1e12, round(f0/self.frequency_scale, 2)



class RH_parameters:

	def __init__(self, fab_parameters, device_parameters):

		self.module = 'RH_parameters'
		self.version = '1.0.0'

		self.Z0 = 50
		self.epsilon0 = cst.epsilon_0
		self.k_b = cst.k #J/K
		self.e = cst.e #C
		self.hbar = cst.hbar #J*s
		self.h = cst.h #J*s
		self.phi0 = self.hbar/(2*self.e) #Wb
		self.Delta0 = 210.*1e-6 #V

		self.buisson_factor = fab_parameters['junction_parameters']['buisson_factor']
		self.heating_factor = fab_parameters['junction_parameters']['heating_factor']
		self.c_j = fab_parameters['junction_parameters']['capacitance_per_unit_area']*1e-3 #F/m^2
		self.j_c = fab_parameters['junction_parameters']['critical_current_density']*1e4 #A/m^2
		self.c_c = fab_parameters['capacitor_parameters']['capacitance_per_unit_area']*1e-3 #F/m^2
		self.Wj = device_parameters['junction_parameters']['width_of_junction']*1e-6 #m
		self.Hj = device_parameters['junction_parameters']['height_of_junction']*1e-6 #m
		self.Njj = device_parameters['junction_parameters']['number_of_junctions_per_unit_cell']
		self.Ncapa = device_parameters['capacitor_parameters']['number_of_capacitors_per_unit_cell']
		self.Ncell = device_parameters['TWPA_parameters']['number_of_cells']
		self.Np = device_parameters['TWPA_parameters']['modulation_period']
		self.eta = device_parameters['TWPA_parameters']['modulation_amplitude_percent']
		self.frequency_scale = 1e9


	def get_params(self, **kwargs):

		if 'modulation' in kwargs:
			modulation = kwargs.get("modulation")
		else:
			modulation = False
		if 'print_params' in kwargs:
			print_params = kwargs.get("print_params")
		else:
			print_params = False

		### Junction area
		Aj = self.Wj*self.Hj

		### Junction resistance at room temperature
		Rj = np.pi*self.Delta0/(2*Aj*self.j_c*self.buisson_factor)

		### Critical current
		Ic = Aj*self.j_c/self.heating_factor

		### Junction normal state resistance
		Rn = np.pi*self.Delta0/(2*Ic)

		### Josephson Capacitance
		Cj = Aj*self.c_j

		### Josephson Inductance
		Lj = (self.phi0/Ic)

		### Inductance of one unit cell
		Lj_cell = self.Njj*Lj

		### Capacitance of one unit cell
		Cj_cell = Cj/self.Njj

		### Ground capacitance
		Cg = Lj_cell/(self.Z0**2)

		### Capacitor dimensions
		A_capa = Cg/self.c_c

		### Junction plasma frequency
		fj = 1/(2*np.pi*np.sqrt(Lj_cell*Cj_cell))

		### Cut-off frequency
		f0 = 1/(2*np.pi*np.sqrt(Lj_cell*Cg))

		### Gap frequency
		fg = np.sqrt(((np.pi*f0*fj)**2)/((np.pi*f0)**2+(self.Np*fj)**2))

		if print_params:
			print('Junction capacitance per unit area: c_j = %.2f fF/um^2' %(self.c_j*1e3))
			print('Junction critical current density: j_c = %.2f A/cm^2' %(self.j_c*1e-4))
			print('Capacitor capacitance per unit area: c_c = %.2f fF/um^2' %(self.c_c*1e3))
			print('Number of cells: Ncell = %.f' %(self.Ncell))
			print('Number of junctions per cell: Njj = %.f' %(self.Njj))
			print('Number of capacitors per cell: Ncapa = %.f' %(self.Ncapa))
			print('Junction dimensions: H = %.2f um | W = %.2f um | A = %.2f um^2' %(self.Hj*1e6, self.Wj*1e6, Aj*1e12))
			print('Room temp resistance: Rj = %.2f Ohm' %(Rj))
			print('Critical current: Ic = %.2f uA' %(Ic*1e6))
			print('Normal state resistance: Rn = %.2f Ohm' %(Rn))
			print('Josephson inductance: Lj = %.2f pH' %(Lj*1e12))
			print('Josephson capacitance: Cj = %.2f fF' %(Cj*1e15))
			print('Josephson inductance per unit cell: Lj_cell = %.2f pH' %(Lj_cell*1e12))
			print('Josephson capacitance per unit cell: Cj_cell = %.2f fF' %(Cj_cell*1e15))
			print('Ground capacitance to get 50 Ohm matching: Cg = %.2f fF' %(Cg*1e15))
			print('Capacitor area: A = %.2f um^2' %(A_capa*1e12))
			print ('Plasma frequency: fj = %.2f GHz' %(fj/self.frequency_scale))
			print ('Cut-off frequency: f0 = %.2f GHz' %(f0/self.frequency_scale))
			if modulation:
				print('Modulation period: Np = %.f' %(self.Np))
				print('Modulation amplitude: eta = %.f%%' %(self.eta))
				print ('Gap frequency: fgap = %.2f GHz' %(fg/self.frequency_scale))
			else:
				print('No modulation')

		return A_capa*1e12


class SJ_parameters:

	def __init__(self, fab_parameters, device_parameters):

		self.module = 'SJ_parameters'
		self.version = '1.0.0'

		self.Z0 = 50
		self.epsilon0 = cst.epsilon_0
		self.k_b = cst.k #J/K
		self.e = cst.e #C
		self.hbar = cst.hbar #J*s
		self.h = cst.h #J*s
		self.phi0 = self.hbar/(2*self.e) #Wb
		self.Delta0 = 210.*1e-6 #V

		self.buisson_factor = fab_parameters['junction_parameters']['buisson_factor']
		self.heating_factor = fab_parameters['junction_parameters']['heating_factor']
		self.c_j = fab_parameters['junction_parameters']['capacitance_per_unit_area']*1e-3 #F/m^2
		self.j_c = fab_parameters['junction_parameters']['critical_current_density']*1e4 #A/m^2
		self.Wj = device_parameters['junction_parameters']['width_of_junction']*1e-6 #m
		self.Hj = device_parameters['junction_parameters']['height_of_junction']*1e-6 #m
		self.Njj = device_parameters['junction_parameters']['number_of_junctions_per_unit_cell']
		self.Ncell = device_parameters['TWPA_parameters']['number_of_cells']
		self.Np = device_parameters['TWPA_parameters']['modulation_period']
		self.eta = device_parameters['TWPA_parameters']['modulation_amplitude_percent']
		self.frequency_scale = 1e9


	def get_params(self, **kwargs):

		if 'modulation' in kwargs:
			modulation = kwargs.get("modulation")
		else:
			modulation = False
		if 'print_params' in kwargs:
			print_params = kwargs.get("print_params")
		else:
			print_params = False

		### Junction area
		Aj = self.Wj*self.Hj

		### Junction resistance at room temperature
		Rj = np.pi*self.Delta0/(2*Aj*self.j_c*self.buisson_factor)

		### Critical current
		Ic = Aj*self.j_c/self.heating_factor

		### Junction normal state resistance
		Rn = np.pi*self.Delta0/(2*Ic)

		### Josephson Capacitance
		Cj = Aj*self.c_j

		### Josephson Inductance
		Lj = (self.phi0/Ic)

		### Inductance of one unit cell
		Lj_cell = self.Njj*Lj

		### Capacitance of one unit cell
		Cj_cell = Cj/self.Njj

		### Ground capacitance
		Cg = Lj_cell/(self.Z0**2)

		### Junction plasma frequency
		fj = 1/(2*np.pi*np.sqrt(Lj_cell*Cj_cell))

		### Cut-off frequency
		f0 = 1/(2*np.pi*np.sqrt(Lj_cell*Cg))

		### Gap frequency
		fg = np.sqrt(((np.pi*f0*fj)**2)/((np.pi*f0)**2+(self.Np*fj)**2))

		if print_params:
			print('Junction capacitance per unit area: c_j = %.2f fF/um^2' %(self.c_j*1e3))
			print('Junction critical current density: j_c = %.2f A/cm^2' %(self.j_c*1e-4))
			print('Number of cells: Ncell = %.f' %(self.Ncell))
			print('Number of junctions per cell: Njj = %.f' %(self.Njj))
			print('Junction dimensions: H = %.2f um | W = %.2f um | A = %.2f um^2' %(self.Hj*1e6, self.Wj*1e6, Aj*1e12))
			print('Room temp resistance: Rj = %.2f Ohm' %(Rj))
			print('Critical current: Ic = %.2f uA' %(Ic*1e6))
			print('Normal state resistance: Rn = %.2f Ohm' %(Rn))
			print('Josephson inductance: Lj = %.2f pH' %(Lj*1e12))
			print('Josephson capacitance: Cj = %.2f fF' %(Cj*1e15))
			print('Josephson inductance per unit cell: Lj_cell = %.2f pH' %(Lj_cell*1e12))
			print('Josephson capacitance per unit cell: Cj_cell = %.2f fF' %(Cj_cell*1e15))
			print('Ground capacitance to get 50 Ohm matching: Cg = %.2f fF' %(Cg*1e15))
			print ('Plasma frequency: fj = %.2f GHz' %(fj/self.frequency_scale))
			print ('Cut-off frequency: f0 = %.2f GHz' %(f0/self.frequency_scale))
			if modulation:
				print('Modulation period: Np = %.f' %(self.Np))
				print('Modulation amplitude: eta = %.f%%' %(self.eta))
				print ('Gap frequency: fgap = %.2f GHz' %(fg/self.frequency_scale))
			else:
				print('No modulation')

		return Cg
	

class SNAIL_parameters:

	def __init__(self, fab_parameters, device_parameters):

		self.module = 'SNAIL_parameters'
		self.version = '1.0.0'

		self.Z0 = 50
		self.epsilon0 = cst.epsilon_0
		self.k_b = cst.k #J/K
		self.e = cst.e #C
		self.hbar = cst.hbar #J*s
		self.h = cst.h #J*s
		self.phi0 = self.hbar/(2*self.e) #Wb
		self.Delta0 = 210.*1e-6 #V
		self.eps_AlOx_ALD = 9.8

		self.buisson_factor = fab_parameters['junction_parameters']['buisson_factor']
		self.heating_factor = fab_parameters['junction_parameters']['heating_factor']
		self.c_j = fab_parameters['junction_parameters']['capacitance_per_unit_area']*1e-3 #F/m^2
		self.j_c_large = fab_parameters['junction_parameters']['critical_current_density_low_ox_large_JJ']*1e4 #A/m^2
		self.j_c_small = fab_parameters['junction_parameters']['critical_current_density_low_ox_small_JJ']*1e4 #A/m^2
		self.Wj_large = device_parameters['large_junction_parameters']['width_of_junction']*1e-6 #m
		self.Hj_large = device_parameters['large_junction_parameters']['height_of_junction']*1e-6 #m
		self.N_large_JJ = device_parameters['large_junction_parameters']['number_of_large_junctions_in_the_SNAIL']
		self.Wj_small = device_parameters['small_junction_parameters']['width_of_junction']*1e-6 #m
		self.Hj_small = device_parameters['small_junction_parameters']['height_of_junction']*1e-6 #m
		self.fixed_dimension_small_JJ = device_parameters['small_junction_parameters']['fixed_dimension']
		self.r_ratio = device_parameters['small_junction_parameters']['critical_current_ratio_large_small']
		self.Cg_pads_width = device_parameters['ground_capacitance_pads_parameters']['width_of_pads']*1e-6 #m
		self.diel_thickness = device_parameters['ground_capacitance_pads_parameters']['ALD_diel_thickness_nm']*1e-9 #m
		self.flux_matching = device_parameters['ground_capacitance_pads_parameters']['flux_impedance_matching']
		self.loop_area = device_parameters['loop_parameters']['loop_area']*1e-12 #m^2
		self.Njj = device_parameters['large_junction_parameters']['number_of_SNAILs_per_unit_cell']
		self.Ncell = device_parameters['TWPA_parameters']['number_of_cells']
		self.Np = device_parameters['TWPA_parameters']['modulation_period']
		self.eta = device_parameters['TWPA_parameters']['modulation_amplitude_percent']
		self.frequency_scale = 1e9

	def calc_alpha_gamma_tilde(self,Phi_s, flux, r_ratio):

		alpha_tilde = r_ratio*np.cos(Phi_s) + 1/self.N_large_JJ * np.cos((Phi_s - flux)/(self.N_large_JJ))
			
		beta_tilde = 1/2 * (r_ratio*np.sin(Phi_s) + 1/self.N_large_JJ**2 * np.sin((Phi_s - flux)/(self.N_large_JJ)))

		gamma_tilde = 1/6 * (r_ratio*np.cos(Phi_s) + 1/self.N_large_JJ**3 * np.cos((Phi_s - flux)/(self.N_large_JJ)))

		return alpha_tilde, beta_tilde, gamma_tilde
	
	def I_phase(self,Phi_s, flux,Ic,r_ratio): 

		return r_ratio*Ic*np.sin(Phi_s) + Ic*np.sin((Phi_s - flux)/(self.N_large_JJ))
	
	def Phi_s_for_sim_SNAIL(self,flux,Ic,r_ratio):

		Phi_s = optimization.fsolve(self.I_phase, x0 = flux, args = (flux,Ic,r_ratio))[0]
		return Phi_s

	def calculate_total_area_to_gnd(self, large_JJ_area, flux_matching, Ic_r_ratio):

		Ic_large = large_JJ_area*self.j_c_large/self.heating_factor

		Lj_large = (self.phi0/Ic_large)

		try:
			if len(Ic_large) != 0:
				phi_s = np.array([self.Phi_s_for_sim_SNAIL(flux_matching * 2*np.pi, Ic, Ic_r_ratio) for Ic in Ic_large])
		
		except:

			phi_s = self.Phi_s_for_sim_SNAIL(flux_matching * 2*np.pi, Ic_large, Ic_r_ratio)

		alpha_tilde, _, _ = self.calc_alpha_gamma_tilde(phi_s, flux_matching * 2 * np.pi, Ic_r_ratio)

		Lj_cell = Lj_large/alpha_tilde
		Cg = Lj_cell/(self.Z0**2)

		total_ground_area = self.diel_thickness * Cg / (self.epsilon0 * self.eps_AlOx_ALD)

		return total_ground_area*1e12, Cg, Lj_cell


	def get_params(self, **kwargs):

		if 'modulation' in kwargs:
			modulation = kwargs.get("modulation")
		else:
			modulation = False
		if 'print_params' in kwargs:
			print_params = kwargs.get("print_params")
		else:
			print_params = False

		### Junction area
		Aj_large = self.Wj_large*self.Hj_large

		### Junction resistance at room temperature
		Rj_large = np.pi*self.Delta0/(2*Aj_large*self.j_c_large*self.buisson_factor)

		### Critical current
		Ic_large = Aj_large*self.j_c_large/self.heating_factor

		Ic_small = self.r_ratio*Ic_large

		Aj_small = Ic_small*self.heating_factor/self.j_c_small

		area_ratio = Aj_small / Aj_large

		if self.fixed_dimension_small_JJ == 'Height':

			Wj_small = Aj_small/self.Hj_small
			Hj_small = self.Hj_small
		
		elif self.fixed_dimension_small_JJ == 'Width':

			Hj_small = Aj_small/self.Wj_small
			Wj_small = self.Wj_small

		else:
			raise ValueError('Provide a fixed dimension for the small JJ as Height or Width')



		Rj_small = np.pi*self.Delta0/(2*Aj_small*self.j_c_small*self.buisson_factor)

		### Junction normal state resistance
		Rn_large = np.pi*self.Delta0/(2*Ic_large)

		Rn_small = np.pi*self.Delta0/(2*Ic_small)

		### Josephson Capacitance
		Cj_large = Aj_large*self.c_j

		Cj_small = Aj_small*self.c_j

		### Josephson Inductance
		Lj_large = (self.phi0/Ic_large)

		### Inductance of one unit cell

		# def I_phase(Phi_s, flux): 

		# 	return self.r_ratio*Ic_large*np.sin(Phi_s) + Ic_large*np.sin((Phi_s - flux)/(3))

		# def Phi_s_for_sim_SNAIL(flux):
		# 	Phi_s = optimization.fsolve(I_phase, x0 = flux, args = (flux))[0]
		# 	return Phi_s


		# def calc_alpha_gamma_tilde(Phi_s, flux):

		# 	alpha_tilde = self.r_ratio*np.cos(Phi_s) + 1/3 * np.cos((Phi_s - flux)/(3))
			
		# 	beta_tilde = 1/2 * (self.r_ratio*np.sin(Phi_s) + 1/9 * np.sin((Phi_s - flux)/(3)))

		# 	gamma_tilde = 1/6 * (self.r_ratio*np.cos(Phi_s) + 1/27 * np.cos((Phi_s - flux)/(3)))

		# 	return alpha_tilde, beta_tilde, gamma_tilde
		
		
		# Phi_s = Phi_s_for_sim_SNAIL(self.flux_matching * 2*np.pi)

		# alpha_tilde, _, _ = calc_alpha_gamma_tilde(Phi_s, self.flux_matching * 2 * np.pi)

		# Lj_cell = Lj_large/alpha_tilde

		### Capacitance of one unit cell
		Cj_cell = Cj_large/self.N_large_JJ + Cj_small

		### Ground capacitance
		# Cg = Lj_cell/(self.Z0**2)

		total_ground_area, Cg, Lj_cell = self.calculate_total_area_to_gnd(Aj_large, self.flux_matching, self.r_ratio)

		### Junction plasma frequency
		fj = 1/(2*np.pi*np.sqrt(Lj_cell*Cj_cell))

		### Cut-off frequency
		f0 = 1/(2*np.pi*np.sqrt(Lj_cell*Cg))

		### Gap frequency
		fg = np.sqrt(((np.pi*f0*fj)**2)/((np.pi*f0)**2+(self.Np*fj)**2))

		if print_params:
			print('Junction capacitance per unit area: c_j = %.2f fF/um^2' %(self.c_j*1e3))
			print('Large junction critical current density: j_c = %.2f A/cm^2' %(self.j_c_large*1e-4))
			print('Small junction critical current density: j_c = %.2f A/cm^2' %(self.j_c_small*1e-4))
			print('Number of cells: Ncell = %.f' %(self.Ncell))
			print('Number of large junctions in SNAIL: Njj = %.f' %(self.N_large_JJ))
			print('Number of junctions per cell: Njj = %.f' %(self.Njj))
			print('Large Junction dimensions: H = %.2f um | W = %.2f um | A = %.2f um^2' %(self.Hj_large*1e6, self.Wj_large*1e6, Aj_large*1e12))
			print('Small Junction dimensions: H = %.2f um | W = %.2f um | A = %.2f um^2' %(Hj_small*1e6, Wj_small*1e6, Aj_small*1e12))
			# print('Room temp resistance: Rj = %.2f Ohm' %(Rj))
			print('Critical current ratio: r_Ic = %.2f ' %(self.r_ratio))
			print('Area ratio: r_A = %.2f ' %(area_ratio))
			print('Critical current large: Ic = %.2f uA' %(Ic_large*1e6))
			print('Critical current small: Ic = %.2f uA' %(Ic_small*1e6))
			# print('Normal state resistance: Rn = %.2f Ohm' %(Rn))
			# print('Josephson inductance: Lj = %.2f pH' %(Lj*1e12))
			# print('Josephson capacitance: Cj = %.2f fF' %(Cj*1e15))
			print(r'Josephson inductance per unit cell: Lj_cell @ %.2f $\Phi_0$ = %.2f pH' %(self.flux_matching, Lj_cell*1e12))
			print('Josephson capacitance per unit cell: Cj_cell = %.2f fF' %(Cj_cell*1e15))
			print('Ground capacitance to get 50 Ohm matching: Cg = %.2f fF' %(Cg*1e15))
			print('Total area to ground: %.2f um^2' %(total_ground_area))
			print ('Plasma frequency: fj = %.2f GHz' %(fj/self.frequency_scale))
			print ('Cut-off frequency: f0 = %.2f GHz' %(f0/self.frequency_scale))
			if modulation:
				print('Modulation period: Np = %.f' %(self.Np))
				print('Modulation amplitude: eta = %.f%%' %(self.eta))
				print ('Gap frequency: fgap = %.2f GHz' %(fg/self.frequency_scale))
			else:
				print('No modulation')

		return Cg, total_ground_area, Hj_small*1e6, Wj_small*1e6, area_ratio
