import os
import glob
import numpy as np
import gdstk
import marker_GDS_generator as marker_GDS_generator_cls
import TWPA_assembly as TWPA_assembly_cls
import TWPA_parameters as TWPA_parameters_cls
import JobFileGen as JobFileGen_cls
import importlib
import json





class CAD_manager():

	def __init__(self, date, WaferName, WaferNumber):

		self.module = 'CAD_manager'
		self.version = '1.0.0'

		dir_path = os.path.dirname(os.path.realpath(__file__))
		self.installation_dir = dir_path+'/'


		fab_param_filename = os.path.join(dir_path, 'default_parameters\\fab_parameters.json')
		with open(fab_param_filename) as json_file:
			self.fab_parameters_dict = json.load(json_file)

		device_param_filename = os.path.join(dir_path, 'default_parameters\\device_parameters.json')
		with open(device_param_filename) as json_file:
			self.device_parameters_dict = json.load(json_file)
		 
		

		# writing options
		self.grid_dim = (4,4) # number of devices
		self.grid_size = (8,8) # size of each device
		self.write_field = 0.25 # write(main) field to be used for lithography

		self.load_reset_libs()

		self.junk_folder = 'junk//'
		self.designs_folder = 'design_files//'
		self.job_batch_files = 'job_batch_files//'

		self.create_clean_folders()

		# options for creating jobs
		self.directory_server = date
		self.directory_client = date + '_' +'Wf' + WaferNumber + '_' + WaferName
		self.dev_label_prefix = None

		self.date = date
		self.WaferNumber = WaferNumber
		self.WaferName = WaferName
		self.device_type = None
		self.chip = None

		self.dev_label = None
		self.design_filename = None

		self.origin_shift = True
		self.write_field_shift = True

		# options for modulation
		self.modulation = None


	def load_reset_libs(self):

		importlib.reload(TWPA_assembly_cls)
		importlib.reload(JobFileGen_cls)
		self.assembly = TWPA_assembly_cls.TWPA_assembly()
		self.JobFileGen = JobFileGen_cls.JobFileGen()
		self.JobFileGen.grid_size = self.grid_size
		self.JobFileGen.grid_dim = self.grid_dim
		self.JobFileGen.write_field = self.write_field



	def create_clean_folders(self, **kwargs):

		junk_folder = self.junk_folder
		designs_folder = self.designs_folder
		job_batch_files = self.job_batch_files

		try:
			os.mkdir(junk_folder)
		except OSError as error:
			if '[WinError 183] Cannot create a file when that file already exists' in str(error):
				print('Junk folder already exists, cleaning it...')
				files = glob.glob(junk_folder+'*')
				for f in files:
					os.remove(f)
			elif '[WinError 183] Impossible de créer un fichier déjà existant:' in str(error):
				print('Junk folder already exists, cleaning it...')
				files = glob.glob(junk_folder+'*')
				for f in files:
					os.remove(f)
			else:
				print(error)
		try:
			os.mkdir(designs_folder)
		except OSError as error:
			if '[WinError 183] Cannot create a file when that file already exists' in str(error):
				pass
			elif '[WinError 183] Impossible de créer un fichier déjà existant:' in str(error):
				pass
			else:
				print(error)

		try:
			os.mkdir(job_batch_files)
		except OSError as error:
			if '[WinError 183] Cannot create a file when that file already exists' in str(error):
				print('Job folder already exists, cleaning it...')
				files = glob.glob(job_batch_files+'*')
				for f in files:
					os.remove(f)
			elif '[WinError 183] Impossible de créer un fichier déjà existant:' in str(error):
				print('Junk folder already exists, cleaning it...')
				files = glob.glob(job_batch_files+'*')
				for f in files:
					os.remove(f)
			else:
				print(error)


	def generate_markers(self, **kwargs):

		self.wafer_radius = 25.4			# for 2 inch wafer
		self.wafer_cut_length = 15			# might need to be adjusted for every batch
		self.markers = marker_GDS_generator_cls.marker_GDS_generator(self.wafer_radius,self.wafer_cut_length)

		self.markers.grid_dim = self.grid_dim
		self.markers.grid_size = self.grid_size
		self.markers.write_field = self.write_field
		self.markers.add_date = True		# add a date stamp (outside chips space)
		self.markers.date = self.date		# override date with custom string
		self.markers.add_parameters = True	# add parameters used for generating GDS (outside chips space)
		self.markers.label_chip = 'Wf' + str(self.WaferNumber)	# label on the top left corner of each chip
		self.markers.label = self.WaferName + '_Wf' + str(self.WaferNumber)	# label outside of the chips space with date and add_parameters 

		self.markers.save_markers(self.designs_folder+'markers-' + self.WaferName + '_Wf' + str(self.WaferNumber) + '.gds')


	def generate_modulated_array(self, **kwargs):
		
		### This function generate the array with modulated cells that will be passed to the assembly class
		

		n = np.arange(0,self.modulation_period,1)

		modulation_arr = (1+(self.modulation_amplitude_percent/100)*np.cos(2*np.pi*n/self.modulation_period))

		if self.device_type in ('LH','RH','CRLH_V01','CRLH_V02','CRLH_V03','CRLH_V04','SJ'):

			area_jj_arr = self.element.height_jj*self.element.width_jj*modulation_arr.reshape(int(self.modulation_period/self.element.cells_in_element),self.element.cells_in_element)

			if self.device_type in ('LH','RH','CRLH_V01','CRLH_V02','CRLH_V03','CRLH_V04'):
				area_capa_arr = self.element.area_capa*modulation_arr.reshape(int(self.modulation_period/self.element.cells_in_element),self.element.cells_in_element)

			element_arr = []
			for i in range(len(area_jj_arr)):
				self.element.height_jj = area_jj_arr[i]/self.element.width_jj
				if self.device_type in ('LH','RH','CRLH_V01','CRLH_V02','CRLH_V03','CRLH_V04'):
					self.element.area_capa = area_capa_arr[i]
				element_arr.append(self.element.generateCell())

			### Back to average value to create the test chain elements
			self.element.height_jj = np.mean(area_jj_arr/self.element.width_jj)
			if self.device_type in ('LH','RH','CRLH_V01','CRLH_V02','CRLH_V03','CRLH_V04'):
				self.element.area_capa = np.mean(area_capa_arr)

		elif self.device_type == 'SNAIL':
			
			importlib.reload(TWPA_parameters_cls)
			self.SNAIL_parameters = TWPA_parameters_cls.SNAIL_parameters(self.fab_parameters_dict, self.device_parameters_dict[self.device_type])

			self.element.modulation = 'True'

			init_width_large_jj = self.element.width_jj_large
			init_width_small_jj = self.element.width_jj_small
			init_height_large_jj = self.element.height_jj_large
			init_height_small_jj = self.element.height_jj_small

			if self.element.keep_Z_constant_with_modulation == 'True':

				area_large_jj_arr = self.element.height_jj_large*self.element.width_jj_large*modulation_arr.reshape(int(self.modulation_period/self.element.cells_in_element),self.element.cells_in_element)
				area_large_jj_arr_for_calc = self.element.height_jj_large*self.element.width_jj_large*modulation_arr
				area_small_jj_arr = self.element.height_jj_small*self.element.width_jj_small*modulation_arr.reshape(int(self.modulation_period/self.element.cells_in_element),self.element.cells_in_element)


				height_large_jj_arr = area_large_jj_arr/self.element.width_jj_large
				height_small_jj_arr = area_small_jj_arr/self.element.width_jj_small


				# We re-calculate the pads height for capacitance to ground because the total metallic area changes due to the change of JJ heights (and thus the inductance of the loop).

				upper_area = self.element.number_of_large_junctions * (self.element.width_jj_large + self.element.spacing_jj_large/2) * (2*self.element.electrode_height_difference_jj + height_large_jj_arr) + self.element.number_of_large_junctions * height_large_jj_arr * self.element.spacing_jj_large/2

				loop_bridges_area = self.element.loop_arm_width*self.element.loop_height + self.element.loop_arm_width*(self.element.loop_height + height_large_jj_arr + 2*self.element.electrode_height_difference_jj)

				lower_area = (self.element.loop_width + self.element.loop_arm_width)*(height_small_jj_arr + 2*self.element.electrode_height_difference_jj) - 2*self.element.electrode_height_difference_jj*(self.element.spacing_jj_large/2 - self.element.litho_overlap/2)

				total_ground_area, _, _  = self.SNAIL_parameters.calculate_total_area_to_gnd(area_large_jj_arr_for_calc*1e-12, self.SNAIL_parameters.flux_matching, self.SNAIL_parameters.r_ratio)
				
				pads_area = total_ground_area.reshape(int(self.modulation_period/self.element.cells_in_element),self.element.cells_in_element) - (upper_area + loop_bridges_area + lower_area)

				height_capacitance_pad_arr = (pads_area/(4*self.element.ground_capacitance_pads_width))
			
			elif self.element.modulate_capa_only == 'True':

				area_large_jj_arr = (self.element.height_jj_large*self.element.width_jj_large*np.ones(len(modulation_arr))).reshape(int(self.modulation_period/self.element.cells_in_element),self.element.cells_in_element)

				area_small_jj_arr = (self.element.height_jj_small*self.element.width_jj_small*np.ones(len(modulation_arr))).reshape(int(self.modulation_period/self.element.cells_in_element),self.element.cells_in_element)

				height_capacitance_pad_arr = self.element.ground_capacitance_pads_height*modulation_arr.reshape(int(self.modulation_period/self.element.cells_in_element),self.element.cells_in_element)
			
			else:

				area_large_jj_arr = self.element.height_jj_large*self.element.width_jj_large*modulation_arr.reshape(int(self.modulation_period/self.element.cells_in_element),self.element.cells_in_element)
				area_small_jj_arr = self.element.height_jj_small*self.element.width_jj_small*modulation_arr.reshape(int(self.modulation_period/self.element.cells_in_element),self.element.cells_in_element)
				height_capacitance_pad_arr = (self.element.ground_capacitance_pads_height*np.ones(len(modulation_arr))).reshape(int(self.modulation_period/self.element.cells_in_element),self.element.cells_in_element)


			element_arr = []

			for i in range(len(area_large_jj_arr)):

				self.element.height_jj_large = area_large_jj_arr[i]/self.element.width_jj_large
				self.element.height_jj_small = area_small_jj_arr[i]/self.element.width_jj_small
				self.element.ground_capacitance_pads_height = height_capacitance_pad_arr[i]

				element_arr.append(self.element.generateCell())

			### Back to average value to create the test chain elements
			self.element.modulation = 'False'
			self.element.height_jj_large = np.mean(area_large_jj_arr/init_width_large_jj)
			self.element.height_jj_small = np.mean(area_small_jj_arr/init_width_small_jj)
			self.element.ground_capacitance_pads_height = np.mean(height_capacitance_pad_arr) # Not actually used

		self.element.generateCell()

		return element_arr


	def generate_GDS(self, **kwargs):

		if 'change_area_capa' in kwargs:
			change_area_capa = kwargs.get("change_area_capa")
		else:
			change_area_capa = False
		if 'rotate' in kwargs:
			rotate = kwargs.get("rotate")
		else:
			rotate = False

		self.assembly.wafer_label = 'Wf' + str(self.WaferNumber) + '-' + self.chip
		self.assembly.device = self.device_type
		self.assembly.grid_size = self.grid_size # change here the size of the chips between (8,8) and (8,4)
		self.assembly.write_field = self.write_field
		if self.modulation:
			self.assembly.modulation = self.modulation
			self.assembly.modulation_period = self.modulation_period
			self.assembly.element_arr = self.generate_modulated_array()
		if change_area_capa:
			self.assembly.unit_cell = self.element.generateCell(change_area_capa=change_area_capa)
		elif self.device_type!='feedline':
			self.assembly.unit_cell = self.element.generateCell()

		if self.device_type!='feedline':
			self.assembly.unit_cell_size = self.element.x_size_of_cell

		if self.device_type in ('LH','RH','CRLH_V01','CRLH_V02','CRLH_V03','CRLH_V04'):
			self.assembly.unit_cell_size_tot = self.element.x_size_of_cell_tot
			
		if self.device_type!='feedline':
			self.assembly.unit_cell_height = self.element.y_size_of_cell
			self.assembly.cells_in_element = self.element.cells_in_element
			self.assembly.n_unit_cells = int(self.n_unit_cells)

		self.assembly.add_label = True
		self.assembly.position_label = 'bottom_left'
		self.assembly.add_logo_CNRS = False
		self.assembly.add_logo_Neel = False
		self.assembly.add_R4t_Al = True

		if self.device_type in ('LH','RH'):
			self.assembly.generate_test_chains_jj = True
			self.assembly.generate_test_chains_capa = True
			self.assembly.generate_test_chains_SNAIL = False
			self.assembly.add_wet_etching_test = True
			self.assembly.unit_cell_jj = self.element.JJ
			self.assembly.x_size_jj = self.element.x_size_of_jj
			self.assembly.y_size_jj = self.element.y_size_of_jj
			self.assembly.spacing_jj = self.element.spacing_jj
			self.assembly.jj_top_layer = self.element.jj_top_layer
			self.assembly.unit_cell_capa = self.element.PPC
			self.assembly.x_size_capa = self.element.x_size_of_capa
			self.assembly.y_size_capa = self.element.y_size_of_capa
			self.assembly.spacing_capa = self.element.spacing_capa
			self.assembly.capa_top_layer = self.element.capa_top_layer 
			self.assembly.jj_bottom_layer = self.element.jj_bottom_layer
			self.assembly.capa_bottom_layer = self.element.capa_bottom_layer

		elif self.device_type == 'CRLH_V01':
			self.assembly.generate_test_chains_jj = True
			self.assembly.generate_test_chains_capa = False
			self.assembly.generate_test_chains_SNAIL = False
			self.assembly.add_wet_etching_test = False
			self.assembly.add_R4t_Al = False
			self.assembly.unit_cell_jj = self.element.JJ_line
			self.assembly.x_size_jj = self.element.x_size_of_jj
			self.assembly.y_size_jj = self.element.y_size_of_jj
			self.assembly.spacing_jj = self.element.spacing_jj_ground
			self.assembly.bottom_spacing_jj = self.element.bottom_spacing_jj_ground
			self.assembly.top_spacing_jj = self.element.top_spacing_jj_ground
			self.assembly.jj_top_layer = self.element.jj_top_layer
			self.assembly.unit_cell_capa = self.element.PPC_line
			self.assembly.x_size_capa = self.element.x_size_of_capa
			self.assembly.y_size_capa = self.element.y_size_of_capa
			self.assembly.spacing_capa = self.element.spacing_capa_line
			self.assembly.bottom_spacing_capa = self.element.bottom_spacing_capa_line
			self.assembly.top_spacing_capa = self.element.top_spacing_capa_line
			self.assembly.capa_top_layer = self.element.capa_top_layer 
			self.assembly.jj_bottom_layer = self.element.jj_bottom_layer
			self.assembly.capa_bottom_layer = self.element.capa_bottom_layer

		elif self.device_type == 'CRLH_V02':
			self.assembly.generate_test_chains_jj = True
			self.assembly.generate_test_chains_capa = False
			self.assembly.generate_test_chains_SNAIL = False
			self.assembly.add_wet_etching_test = False
			self.assembly.add_R4t_Al = False
			self.assembly.unit_cell_jj = self.element.JJ_line
			self.assembly.x_size_jj = self.element.x_size_of_jj
			self.assembly.y_size_jj = self.element.y_size_of_jj
			self.assembly.spacing_jj = self.element.spacing_jj_ground
			self.assembly.bottom_spacing_jj = self.element.bottom_spacing_jj_ground
			self.assembly.top_spacing_jj = self.element.top_spacing_jj_ground
			self.assembly.jj_top_layer = self.element.jj_top_layer
			self.assembly.unit_cell_capa = self.element.PPC_line
			self.assembly.x_size_capa = self.element.x_size_of_capa
			self.assembly.y_size_capa = self.element.y_size_of_capa
			self.assembly.spacing_capa = self.element.spacing_capa_line
			self.assembly.bottom_spacing_capa = self.element.bottom_spacing_capa_line
			self.assembly.top_spacing_capa = self.element.top_spacing_capa_line
			self.assembly.capa_top_layer = self.element.capa_top_layer 
			self.assembly.jj_bottom_layer = self.element.jj_bottom_layer
			self.assembly.capa_bottom_layer = self.element.capa_bottom_layer
		
		elif self.device_type == 'CRLH_V03':
			self.assembly.generate_test_chains_jj = True
			self.assembly.generate_test_chains_capa = False
			self.assembly.generate_test_chains_SNAIL = False
			self.assembly.add_wet_etching_test = False
			self.assembly.add_R4t_Al = False
			self.assembly.unit_cell_jj = self.element.JJ_line
			self.assembly.x_size_jj = self.element.x_size_of_jj
			self.assembly.y_size_jj = self.element.y_size_of_jj
			self.assembly.spacing_jj = self.element.spacing_jj_ground
			self.assembly.bottom_spacing_jj = self.element.bottom_spacing_jj_ground
			self.assembly.top_spacing_jj = self.element.top_spacing_jj_ground
			self.assembly.unit_cell_capa = self.element.PPC_line
			self.assembly.x_size_capa = self.element.x_size_of_capa
			self.assembly.y_size_capa = self.element.y_size_of_capa
			self.assembly.spacing_capa = self.element.spacing_capa_line
			self.assembly.bottom_spacing_capa = self.element.bottom_spacing_capa_line
			self.assembly.top_spacing_capa = self.element.top_spacing_capa_line
			self.assembly.bottom_layer = self.element.bottom_layer
			self.assembly.jj_top_layer = self.element.jj_top_layer
			self.assembly.capa_top_layer = self.element.capa_top_layer

		elif self.device_type == 'CRLH_V04':
			self.assembly.generate_test_chains_jj = True
			self.assembly.generate_test_chains_capa = False
			self.assembly.generate_test_chains_SNAIL = False
			self.assembly.add_wet_etching_test = False
			self.assembly.add_R4t_Al = False
			self.assembly.unit_cell_jj = self.element.JJ_line
			self.assembly.x_size_jj = self.element.x_size_of_jj
			self.assembly.y_size_jj = self.element.y_size_of_jj
			self.assembly.spacing_jj = self.element.spacing_jj_ground
			self.assembly.bottom_spacing_jj = self.element.bottom_spacing_jj_ground
			self.assembly.top_spacing_jj = self.element.top_spacing_jj_ground
			self.assembly.unit_cell_capa = self.element.PPC_line
			self.assembly.x_size_capa = self.element.x_size_of_capa
			self.assembly.y_size_capa = self.element.y_size_of_capa
			self.assembly.spacing_capa = self.element.spacing_capa_line
			self.assembly.bottom_spacing_capa = self.element.bottom_spacing_capa_line
			self.assembly.top_spacing_capa = self.element.top_spacing_capa_line
			self.assembly.bottom_layer = self.element.bottom_layer
			self.assembly.jj_top_layer = self.element.jj_top_layer
			self.assembly.capa_top_layer = self.element.capa_top_layer
			
		elif self.device_type in ('SJ'):
			self.assembly.generate_test_chains_jj = True
			self.assembly.generate_test_chains_capa = False
			self.assembly.generate_test_chains_SNAIL = False
			self.assembly.add_wet_etching_test = False
			self.assembly.unit_cell_jj = self.element.generateCell()
			self.assembly.x_size_jj = self.element.x_size_of_cell
			self.assembly.y_size_jj = self.element.y_size_of_cell
			self.assembly.spacing_jj = self.element.spacing_jj
			self.assembly.jj_top_layer = self.element.jj_top_layer
			self.assembly.jj_bottom_layer = self.element.jj_bottom_layer

		elif self.device_type in ('SNAIL'):
			self.assembly.generate_test_chains_jj = False
			self.assembly.generate_test_chains_capa = False
			self.assembly.generate_test_chains_SNAIL = True
			self.assembly.add_wet_etching_test = False
			self.assembly.x_size_jj = self.element.x_size_of_cell
			self.assembly.y_size_jj = self.element.y_size_of_cell
			self.assembly.unit_cell_jj_small = self.element.JJ_small
			self.assembly.unit_cell_jj_large = self.element.JJ_large
			self.assembly.x_size_jj_large = self.element.x_size_of_large_JJ
			self.assembly.y_size_jj_large = self.element.y_size_of_large_JJ
			self.assembly.x_size_jj_small = self.element.x_size_of_small_JJ
			self.assembly.y_size_jj_small = self.element.y_size_of_small_JJ
			self.assembly.spacing_jj = self.element.spacing_jj_large
			self.assembly.jj_top_layer = self.element.jj_top_layer
			self.assembly.jj_bottom_layer = self.element.jj_bottom_layer

		elif self.device_type == ('LER'):
			self.assembly.generate_test_chains_jj = False
			self.assembly.generate_test_chains_capa = True
			self.assembly.generate_test_chains_SNAIL = False
			self.assembly.add_wet_etching_test = True
			self.feedline.feedline_length -= 2.0*self.assembly.dicing_gap
			self.assembly.feedline = self.feedline.GenerateFeedline()
			self.assembly.feedline_width = self.feedline.feedline_width
			self.assembly.unit_cell = self.resonators
			self.assembly.resonators_coupling_gap = self.resonators_coupling_gap

		elif self.device_type == ('feedline'):
			self.assembly.generate_test_chains_jj = False
			self.assembly.generate_test_chains_capa = False
			self.assembly.generate_test_chains_SNAIL = False
			self.assembly.add_wet_etching_test = True
			self.assembly.add_R4t_Al = False
			self.assembly.add_R4t = True
			self.feedline.feedline_length -= 2.0*self.assembly.dicing_gap
			self.assembly.feedline = self.feedline.GenerateFeedline()
			self.assembly.feedline_width = self.feedline.feedline_width

		self.assembly.ground_layer = self.ground_layer
		self.assembly.pad_bottom_layer = self.pad_bottom_layer
		self.assembly.connection_wire_bottom_layer = self.connection_wire_bottom_layer
		self.assembly.pad_top_layer = self.pad_top_layer
		self.assembly.connection_wire_top_layer = self.connection_wire_top_layer

		if self.dev_label == None:
			self.assembly.dev_label = self.device_type + '_' + self.chip
		else:
			self.assembly.dev_label = self.dev_label
		if self.design_filename == None:
			self.design_filename = self.device_type + '_' + self.chip

		self.assembly.save_location = self.designs_folder + self.design_filename + '.gds'

		self.assembly.installation_dir = self.installation_dir

		if self.device_type == 'LER':
			self.assembly.generate_RES_GDS(rotate=rotate)
		elif self.device_type =='feedline':
			self.assembly.generate_feedline_GDS()
		elif self.device_type =='CRLH_V01':
			self.assembly.generate_TWPA_GDS_inv_microstrip_pad()
		elif self.device_type =='CRLH_V02':
			self.assembly.generate_TWPA_GDS_inv_microstrip_pad()
		elif self.device_type =='CRLH_V03':
			self.assembly.generate_TWPA_GDS_inv_microstrip_pad()
		elif self.device_type =='CRLH_V04':
			self.assembly.generate_TWPA_GDS_inv_microstrip_pad()
		else:
			self.assembly.generate_TWPA_GDS()



	def populate_dose_matric(self, **kwargs):

		self.dose = {}
		active_layers = np.sort(np.array(list(gdstk.gds_info(self.assembly.save_location)['layers_and_datatypes']))[:,0])

		for write_layers_ref in self.litho_plan.keys():

			self.dose[write_layers_ref] = {}

			for layer in active_layers:

				if layer in self.litho_plan[write_layers_ref]:

					self.dose[write_layers_ref][layer] = self.dose_matric[str(layer)]

				else:

					self.dose[write_layers_ref][layer] = 0



	def generate_jobs(self, **kwargs):

		if 'row' in kwargs:
			row = kwargs.get("row")
		else:
			row = 0
		if 'column' in kwargs:
			column = kwargs.get("column")
		else:
			column = 0

		if row+column>0:
			self.JobFileGen.first_run = False
		else:
			self.JobFileGen.first_run = True
		self.JobFileGen.origin_shift = self.origin_shift
		self.JobFileGen.write_field_shift = self.write_field_shift
		self.JobFileGen.junk_folder = self.junk_folder
		self.JobFileGen.directory_client = self.directory_client
		self.JobFileGen.directory_server = self.directory_server

		for write_layers_ref in self.litho_plan.keys():

			self.JobFileGen.WritePositionFile(self.design_filename, write_layers_ref, row, column)
			self.JobFileGen.WriteDoseFile(self.design_filename, write_layers_ref, self.dose[write_layers_ref])



	def generate_batch_files(self, **kwargs):

		for write_layers_ref in self.litho_plan.keys():

			self.JobFileGen.AddSeparator(write_layers_ref)
			self.JobFileGen.AddTerminationCommand(write_layers_ref)

			self.JobFileGen.combine_position_dose(self.job_batch_files, write_layers_ref)

		for litho_cycle in self.batch_plan.keys():

			self.JobFileGen.WriteBatchFile(self.job_batch_files, litho_cycle, self.batch_plan[litho_cycle])