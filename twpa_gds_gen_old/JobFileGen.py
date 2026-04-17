class JobFileGen:

	def __init__(self):

		self.module = 'JobFileGen'
		self.version = '2.0.0'

		# user parameters
		self.user = 'default'

		self.first_run = True
		self.origin_shift = True
		self.write_field_shift = True
		self.junk_folder = None
		self.directory_client = None

		self.grid_size = (8,8)
		self.grid_dim = (4,4)
		self.write_field = 0.25



	def CoordinateFormat(self,position,cord=''):

		return str(int(position))



	def WritePositionFile(self, design_filename, write_layers_ref, row, column, **kwargs):

		job_filename = self.junk_folder + 'position_' + write_layers_ref + '.txt'
		first_run = self.first_run
		directory_client = self.directory_client
		origin_shift = self.origin_shift

		grid_size = self.grid_size
		write_field = self.write_field
		grid_dim = self.grid_dim

		file = open(job_filename, 'a')

		x_00 = (0,0)
		x_01 = (0,(grid_dim[1]*grid_size[1]+4*write_field)*1000)
		x_10 = ((grid_dim[0]*grid_size[0]+4*write_field)*1000,0)
		x_11 = ((grid_dim[0]*grid_size[0]+4*write_field)*1000,(grid_dim[1]*grid_size[1]+4*write_field)*1000)

		x_00_shifted = (0,0)
		x_01_shifted = (0,(grid_dim[1]*grid_size[1]-2*write_field)*1000)
		x_10_shifted = ((grid_dim[0]*grid_size[0]-2*write_field)*1000,0)
		x_11_shifted = ((grid_dim[0]*grid_size[0]-2*write_field)*1000,(grid_dim[1]*grid_size[1]-2*write_field)*1000)

		x_00_local = (write_field*1000,write_field*1000)
		x_01_local = (write_field*1000,(grid_size[1]-write_field)*1000)
		x_10_local = ((grid_size[0]-write_field)*1000,write_field*1000)
		x_11_local = ((grid_size[0]-write_field)*1000,(grid_size[1]-write_field)*1000)

		if self.write_field_shift:

			write_field_shift_val = int(write_field*500)

		else:

			write_field_shift_val = 0

		if origin_shift:

			if first_run:

				file.write('#---------------------------------------------------------\n\n')
				file.write('# Generated using JobFileGen v' + self.version + '\n\n')
				file.write('#---------------------------------------------------------\n\n')
				file.write('# run nbwrite Roch_Nicolas/'+directory_client+'/'+write_layers_ref+' -1=nico:nr1  -2=nico:nr2\n')
				file.write('\n#---------------------------------------------------------\n')
				file.write('.global\n')
				file.write('registration     ('+self.CoordinateFormat(x_01_shifted[0])+' 000, '+self.CoordinateFormat(x_01_shifted[1])+' 000)  ('+self.CoordinateFormat(x_11_shifted[0])+' 000, '+self.CoordinateFormat(x_11_shifted[1])+' 000)\n')
				file.write('registration     ('+self.CoordinateFormat(x_00_shifted[0])+' 000,'+self.CoordinateFormat(x_00_shifted[1])+' 000)   ('+self.CoordinateFormat(x_10_shifted[0])+' 000, '+self.CoordinateFormat(x_10_shifted[1])+' 000)\n')
				file.write('marktype         sqr8N\n')
				file.write('focus            auto\n')
				file.write('.end\n')
				file.write('\n#---------------------------------------------------------\n')

			file.write('\n#'+design_filename+'\n')
			file.write('.block\n')
			file.write('origin			 ('+self.CoordinateFormat(-write_field_shift_val+1000*(-write_field+grid_size[0]*column))+' 000,'+self.CoordinateFormat(-write_field_shift_val+1000*(-write_field+grid_size[1]*row))+' 000)\n')
			file.write('registration     ('+self.CoordinateFormat(write_field_shift_val+x_01_local[0])+' 000, '+self.CoordinateFormat(write_field_shift_val+x_01_local[1])+' 000)  ('+self.CoordinateFormat(write_field_shift_val+x_11_local[0])+' 000, '+self.CoordinateFormat(write_field_shift_val+x_11_local[1])+' 000)\n')
			file.write('registration     ('+self.CoordinateFormat(write_field_shift_val+x_00_local[0])+' 000,'+self.CoordinateFormat(write_field_shift_val+x_00_local[1])+' 000)   ('+self.CoordinateFormat(write_field_shift_val+x_10_local[0])+' 000, '+self.CoordinateFormat(write_field_shift_val+x_10_local[1])+' 000)\n')
			file.write('marktype		 sqr8N\n')
			file.write('focus			 map1\n')
			file.write('stepsize		 ('+self.CoordinateFormat(1000*grid_size[0])+' 000, '+self.CoordinateFormat(1000*grid_size[1])+' 000)\n')
			file.write('grid			 (1, 1)\n')
			file.write('base_dose		 1\n')
			file.write('pattern			 '+design_filename+'			(0, 0)\n')
			file.write('.end\n\n')

		else:

			if first_run:
				
				file.write('#---------------------------------------------------------\n\n')
				file.write('# Generated using JobFileGen v' + self.version + '\n\n')
				file.write('#---------------------------------------------------------\n\n')
				file.write('# run nbwrite Roch_Nicolas/'+directory_client+'/'+write_layers_ref+' -1=nico:nr1  -2=nico:nr2\n')
				file.write('\n#---------------------------------------------------------\n')
				file.write('.global\n')
				file.write('registration     ('+self.CoordinateFormat(x_01[0])+' 000, '+self.CoordinateFormat(x_01[1])+' 000)  ('+self.CoordinateFormat(x_11[0])+' 000, '+self.CoordinateFormat(x_11[1])+' 000)\n')
				file.write('registration     ('+self.CoordinateFormat(x_00[0])+' 000,'+self.CoordinateFormat(x_00[1])+' 000)   ('+self.CoordinateFormat(x_10[0])+' 000, '+self.CoordinateFormat(x_10[1])+' 000)\n')
				file.write('marktype         sqr8N\n')
				file.write('focus            auto\n')
				file.write('.end\n')
				file.write('\n#---------------------------------------------------------\n')

			file.write('\n#'+design_filename+'\n')
			file.write('.block\n')
			file.write('origin			 ('+self.CoordinateFormat(-write_field_shift_val+1000*(2*write_field+grid_size[0]*column))+' 000,'+self.CoordinateFormat(-write_field_shift_val+1000*(2*write_field+grid_size[1]*row))+' 000)\n')
			file.write('registration     ('+self.CoordinateFormat(write_field_shift_val+x_01_local[0])+' 000, '+self.CoordinateFormat(write_field_shift_val+x_01_local[1])+' 000)  ('+self.CoordinateFormat(write_field_shift_val+x_11_local[0])+' 000, '+self.CoordinateFormat(write_field_shift_val+x_11_local[1])+' 000)\n')
			file.write('registration     ('+self.CoordinateFormat(write_field_shift_val+x_00_local[0])+' 000,'+self.CoordinateFormat(write_field_shift_val+x_00_local[1])+' 000)   ('+self.CoordinateFormat(write_field_shift_val+x_10_local[0])+' 000, '+self.CoordinateFormat(write_field_shift_val+x_10_local[1])+' 000)\n')
			file.write('marktype		 sqr8N\n')
			file.write('focus			 map1\n')
			file.write('stepsize		 ('+self.CoordinateFormat(1000*grid_size[0])+' 000, '+self.CoordinateFormat(1000*grid_size[1])+' 000)\n')
			file.write('grid			 (1, 1)\n')
			file.write('base_dose		 1\n')
			file.write('pattern			 '+design_filename+'			(0, 0)\n')
			file.write('.end\n\n')

		file.close()



	def WriteDoseFile(self, design_filename, write_layers_ref, dose):

		job_filename = self.junk_folder + 'dose_' + write_layers_ref + '.txt'
		directory_server = self.directory_server

		file = open(job_filename, 'a')

		# if first:
		# 	file.write('\n\n\n\n\n#---------------------------------------------------------\n')
		# 	file.write('#    Pattern\n')
		# 	file.write('#---------------------------------------------------------\n\n')

		file.write('.pattern\n')
		file.write('id					'+design_filename+'\n')
		file.write('filename			nicolasroch/'+directory_server+'/'+design_filename+'.npf\n\n')

		for layer in dose.keys():
			file.write('dose       '+str(layer)+'        '+str(dose[layer])+'\n')

		file.write('\n.end\n')
		file.write('\n\n')

		file.close()



	def AddSeparator(self, write_layers_ref):
		
		job_filename = self.junk_folder + 'position_' + write_layers_ref + '.txt'
		file = open(job_filename, 'a')

		file.write('\n\n\n\n\n#---------------------------------------------------------\n')
		file.write('#    Pattern\n')
		file.write('#---------------------------------------------------------\n\n')

		file.close()



	def AddTerminationCommand(self, write_layers_ref):

		job_filename = self.junk_folder + 'dose_' + write_layers_ref + '.txt'
		file = open(job_filename, 'a')

		file.write('\n\n\n\n\n.write\n')
		file.write('current			auto\n')
		file.write('.end\n')

		file.close()



	def combine_position_dose(self, job_batch_files, write_layers_ref):

		position_filename = self.junk_folder + 'position_' + write_layers_ref + '.txt'
		dose_filename = self.junk_folder + 'dose_' + write_layers_ref + '.txt'

		filenames = [position_filename, dose_filename]
		with open(job_batch_files+write_layers_ref+'.njf', 'w') as outfile:
		    for fname in filenames:
		        with open(fname) as infile:
		            outfile.write(infile.read())



	def WriteBatchFile(self, job_batch_files, litho_cycle, cycle_plan):

		directory_client = self.directory_client
		batch_filename = 'batch_' + litho_cycle

		jobs_in_cycle = cycle_plan['jobs']
		beam_current = cycle_plan['current']
		sleep = cycle_plan['sleep']
		datum = cycle_plan['datum']

		file = open(job_batch_files+batch_filename+'.nbf', 'a')

		file.write('#---------------------------------------------------------\n\n')
		file.write('#     Generated using JobFileGen v' + self.version + '\n\n')
		file.write('#---------------------------------------------------------\n\n')

		file.write('# run batch Roch_Nicolas/'+directory_client+'/'+batch_filename+'\n')

		for i in range(len(jobs_in_cycle)):

			exposure_job = jobs_in_cycle[i]
			exposure_current = beam_current[i]
			exposure_sleep = sleep[i]
			exposure_datum = datum[i]

			file.write('\n\n\n# ' + exposure_job + '\n\n')
			if exposure_sleep>0:
				file.write('find_db   bc='+str(exposure_current)+'  datum='+str(exposure_datum)+'  L=0\n')
				file.write('sleeps ' + str(int(60*exposure_sleep)) + '\n')
			file.write('run auto_conjugate\n')
			file.write('run nbwrite Roch_Nicolas/'+directory_client+'/'+exposure_job+' -1=nico:nr1  -2=nico:nr2 -r\n')

		file.write('\n\n\n# Back to low current condition\n\n')
		file.write('find_db   bc=1.2  datum=6 L=0\n')
		file.write('run auto_conjugate\n')
		file.write('stage load\n')
		file.write('sleeps 2\n')
		file.write('unloadchuck\n')
		file.write('sleeps 2\n')
		file.write('run check_gun\n')
		file.close()