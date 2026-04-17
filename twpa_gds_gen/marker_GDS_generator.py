
'''

All length inputs are in mm
"***"" Indicates failure possibility


'''

import gdstk
import numpy as np
import datetime


class marker_GDS_generator:

	def __init__(self,wafer_radius,wafer_cut_length):

		self.wafer_radius = wafer_radius
		self.wafer_cut_length = wafer_cut_length

		# user parameters
		self.grid_dim = (4,4)
		self.grid_size = (8,8)
		self.write_field = 0.25
		self.add_date = True
		self.add_parameters = True
		self.date = None
		self.label = None
		self.label_chip = None
		self.text_size = 200

		# do not change these unless you know what you are doing
		self.stroke_width_um = 25
		self.alignment_marker_size_um = 8
		self.global_coord_text_size = 100
		self.outer_boundary_spacing_mult = 2
		self.override_writefield_error = False
		self.place_markers_at_center_of_wf = True


	def save_markers(self,save_location='markers.gds'):

		lib = gdstk.Library()
		cell_save = gdstk.Cell("Markers")
		cell = gdstk.Cell("Markers_tmp")

		wafer_radius_um = self.wafer_radius*1000
		circ = gdstk.ellipse((0,0), wafer_radius_um+self.stroke_width_um/2, inner_radius=wafer_radius_um-self.stroke_width_um/2, layer=10)
		cell.add(circ)

		cut_length_um = self.wafer_cut_length*1000
		y_shift = np.sqrt(self.wafer_radius**2 - (self.wafer_cut_length**2)/4)
		y_shift_um = y_shift*1000
		points = [(-cut_length_um/2,-y_shift_um),(cut_length_um/2,-y_shift_um)]
		cut = gdstk.FlexPath(points, self.stroke_width_um, layer=10, simple_path=True)
		cell.add(cut)

		grid_dim = self.grid_dim
		grid_size = self.grid_size
		write_field = self.write_field

		write_field_um = write_field*1000
		grid_size_um = (grid_size[0]*1000,grid_size[1]*1000)

		global_origin_shift_x_exact = cut_length_um/2
		global_origin_shift_y_exact = y_shift_um
		if self.place_markers_at_center_of_wf:
			global_origin_shift_x_fact = int(global_origin_shift_x_exact/write_field_um)
			# global_origin_shift_x_rec = global_origin_shift_x_exact%int(write_field_um)
			global_origin_shift_y_fact = int(global_origin_shift_y_exact/write_field_um)
			# global_origin_shift_y_rec = global_origin_shift_y_exact%int(write_field_um)
			global_origin_shift_x = (global_origin_shift_x_fact+0.5)*write_field_um
			global_origin_shift_y = (global_origin_shift_y_fact+0.5)*write_field_um
		else:
			print('*** Warning: Markers are not at the center of write field.')
			global_origin_shift_x = global_origin_shift_x_exact
			global_origin_shift_y = global_origin_shift_y_exact

		if int(grid_size[0]*1000)%int(write_field*1000) != 0 or int(grid_size[1]*1000)%int(write_field*1000) != 0:
			if self.override_writefield_error:
				print('*** Downgrading error to warning \n    Error: Grid size is not multiple of write field size.')
			else:
				raise ValueError('Grid size is not multiple of write field size.')

		write_size_um = (grid_dim[0]*grid_size_um[0],grid_dim[1]*grid_size_um[1])



		# place global alignment corner markers

		alignment_marker_size_um = self.alignment_marker_size_um
		outer_boundary_spacing_mult = self.outer_boundary_spacing_mult # in units of write fields

		alignment_marker = gdstk.rectangle((-alignment_marker_size_um/2.0,-alignment_marker_size_um/2.0), (alignment_marker_size_um/2.0,alignment_marker_size_um/2.0), layer=1)
		global_alignment_marker_pos_x = write_size_um[0]/2+outer_boundary_spacing_mult*write_field_um
		global_alignment_marker_pos_y = write_size_um[1]/2+outer_boundary_spacing_mult*write_field_um

		cell.add(alignment_marker.copy().translate(-global_alignment_marker_pos_x,-global_alignment_marker_pos_y))
		cell.add(alignment_marker.copy().translate(-global_alignment_marker_pos_x,global_alignment_marker_pos_y))
		cell.add(alignment_marker.copy().translate(global_alignment_marker_pos_x,global_alignment_marker_pos_y))
		cell.add(alignment_marker.copy().translate(global_alignment_marker_pos_x,-global_alignment_marker_pos_y))



		# add coordinate text

		global_coord_text_size = self.global_coord_text_size

		text00 = gdstk.text('(0,0)', global_coord_text_size, (-global_alignment_marker_pos_x+global_coord_text_size ,-global_alignment_marker_pos_y-global_coord_text_size/2), layer=1)
		cell.add(*text00)
		text10 = gdstk.text('(1,0)', global_coord_text_size, (+global_alignment_marker_pos_x-3.5*global_coord_text_size, -global_alignment_marker_pos_y-global_coord_text_size/2), layer=1)
		cell.add(*text10)
		text01 = gdstk.text('(0,1)', global_coord_text_size, (-global_alignment_marker_pos_x+global_coord_text_size ,+global_alignment_marker_pos_y-global_coord_text_size/2), layer=1)
		cell.add(*text01)
		text11 = gdstk.text('(1,1)', global_coord_text_size, (+global_alignment_marker_pos_x-3.5*global_coord_text_size, +global_alignment_marker_pos_y-global_coord_text_size/2), layer=1)
		cell.add(*text11)



		# add guiding arrows

		arrow_down = gdstk.Polygon([(0,0),(-100,100),(-100,150),(-30,100),(-30,250),(30,250),(30,100),(100,150),(100,100)], layer=1)
		arrow_up = arrow_down.copy().rotate(np.pi)
		arrow_right = arrow_down.copy().rotate(np.pi/2)
		arrow_left = arrow_right.copy().rotate(np.pi)

		num_arrows_y = int(global_alignment_marker_pos_y/1000)
		for j in range(num_arrows_y):
			cell.add(arrow_down.copy().translate(-global_alignment_marker_pos_x,-global_alignment_marker_pos_y+j*1000+500))
			cell.add(arrow_down.copy().translate(global_alignment_marker_pos_x,-global_alignment_marker_pos_y+j*1000+500))
			cell.add(arrow_up.copy().translate(-global_alignment_marker_pos_x,+global_alignment_marker_pos_y-j*1000-500))
			cell.add(arrow_up.copy().translate(global_alignment_marker_pos_x,+global_alignment_marker_pos_y-j*1000-500))

		num_arrows_x = int(global_alignment_marker_pos_x/1000)
		for j in range(num_arrows_x):
			cell.add(arrow_left.copy().translate(-global_alignment_marker_pos_x+j*1000+500,-global_alignment_marker_pos_y))
			cell.add(arrow_left.copy().translate(-global_alignment_marker_pos_x+j*1000+500,global_alignment_marker_pos_y))
			cell.add(arrow_right.copy().translate(global_alignment_marker_pos_x-j*1000-500,-global_alignment_marker_pos_y))
			cell.add(arrow_right.copy().translate(global_alignment_marker_pos_x-j*1000-500,global_alignment_marker_pos_y))

		for j in range(9):
			# cell.add(arrow_right.copy().translate(16400+j*1000+500,0))
			cell.add(arrow_right.copy().translate(global_alignment_marker_pos_x+j*1000+500,0))
			cell.add(arrow_left.copy().translate(-global_alignment_marker_pos_x-(j+1)*1000+500,0))
			cell.add(arrow_up.copy().translate(0,global_alignment_marker_pos_y+j*1000+500))
			if j >= 1:
				cell.add(arrow_down.copy().translate(0,-global_alignment_marker_pos_y-j*1000+500))


		# add marker grids

		for i in range(grid_dim[0]):

			for j in range(grid_dim[1]):

				origin_shift_x = grid_size_um[0]*i-grid_size_um[0]*grid_dim[0]/2
				origin_shift_y = grid_size_um[1]*j-grid_size_um[1]*grid_dim[1]/2

				arrow_marker = gdstk.rectangle((-50,-5),(50,5), layer=1)
				shift_arrow_marker = 100

				# bottom left
				cell.add(alignment_marker.copy().translate(origin_shift_x+write_field_um,origin_shift_y+write_field_um))
				cell.add(alignment_marker.copy().translate(origin_shift_x+2*write_field_um,origin_shift_y+write_field_um))
				cell.add(alignment_marker.copy().translate(origin_shift_x+3*write_field_um,origin_shift_y+write_field_um))
				cell.add(alignment_marker.copy().translate(origin_shift_x+write_field_um,origin_shift_y+2*write_field_um))
				cell.add(alignment_marker.copy().translate(origin_shift_x+write_field_um,origin_shift_y+3*write_field_um))

				cell.add(arrow_marker.copy().rotate(np.pi/4).translate(origin_shift_x+write_field_um-shift_arrow_marker,origin_shift_y+write_field_um-shift_arrow_marker))

				# top left
				cell.add(alignment_marker.copy().translate(origin_shift_x+write_field_um,origin_shift_y+grid_size_um[1]-write_field_um))
				cell.add(alignment_marker.copy().translate(origin_shift_x+2*write_field_um,origin_shift_y+grid_size_um[1]-write_field_um))
				cell.add(alignment_marker.copy().translate(origin_shift_x+3*write_field_um,origin_shift_y+grid_size_um[1]-write_field_um))
				cell.add(alignment_marker.copy().translate(origin_shift_x+write_field_um,origin_shift_y+grid_size_um[1]-2*write_field_um))
				cell.add(alignment_marker.copy().translate(origin_shift_x+write_field_um,origin_shift_y+grid_size_um[1]-3*write_field_um))

				cell.add(arrow_marker.copy().rotate(-np.pi/4).translate(origin_shift_x+write_field_um-shift_arrow_marker,origin_shift_y+grid_size_um[1]-write_field_um+shift_arrow_marker))

				# bottom right
				cell.add(alignment_marker.copy().translate(origin_shift_x+grid_size_um[0]-write_field_um,origin_shift_y+write_field_um))
				cell.add(alignment_marker.copy().translate(origin_shift_x+grid_size_um[0]-2*write_field_um,origin_shift_y+write_field_um))
				cell.add(alignment_marker.copy().translate(origin_shift_x+grid_size_um[0]-3*write_field_um,origin_shift_y+write_field_um))
				cell.add(alignment_marker.copy().translate(origin_shift_x+grid_size_um[0]-write_field_um,origin_shift_y+2*write_field_um))
				cell.add(alignment_marker.copy().translate(origin_shift_x+grid_size_um[0]-write_field_um,origin_shift_y+3*write_field_um))

				cell.add(arrow_marker.copy().rotate(-np.pi/4).translate(origin_shift_x+grid_size_um[0]-write_field_um+shift_arrow_marker,origin_shift_y+write_field_um-shift_arrow_marker))

				# top right
				cell.add(alignment_marker.copy().translate(origin_shift_x+grid_size_um[0]-write_field_um,origin_shift_y+grid_size_um[1]-write_field_um))
				cell.add(alignment_marker.copy().translate(origin_shift_x+grid_size_um[0]-2*write_field_um,origin_shift_y+grid_size_um[1]-write_field_um))
				cell.add(alignment_marker.copy().translate(origin_shift_x+grid_size_um[0]-3*write_field_um,origin_shift_y+grid_size_um[1]-write_field_um))
				cell.add(alignment_marker.copy().translate(origin_shift_x+grid_size_um[0]-write_field_um,origin_shift_y+grid_size_um[1]-2*write_field_um))
				cell.add(alignment_marker.copy().translate(origin_shift_x+grid_size_um[0]-write_field_um,origin_shift_y+grid_size_um[1]-3*write_field_um))

				cell.add(arrow_marker.copy().rotate(np.pi/4).translate(origin_shift_x+grid_size_um[0]-write_field_um+shift_arrow_marker,origin_shift_y+grid_size_um[1]-write_field_um+shift_arrow_marker))


		# add chip labels

		for i in range(grid_dim[0]):

			for j in range(grid_dim[1]):

				origin_shift_x = grid_size_um[0]*i-grid_size_um[0]*grid_dim[0]/2
				origin_shift_y = grid_size_um[1]*j-grid_size_um[1]*grid_dim[1]/2

				device_id = self.label_chip+'-'+str(j)+str(i)
				chip_label = gdstk.text(device_id, self.text_size, (origin_shift_x+write_field_um+241.5,origin_shift_y+write_field_um+7500-429), layer=1)
				cell.add(*chip_label)



		# add dicing markers

		dicing_marker_LB = gdstk.Polygon([(0,0),(75,0),(100,25),(25,25),(25,100),(0,75)], layer=1)
		dicing_marker_TR = dicing_marker_LB.copy().rotate(np.pi)
		dicing_marker_RB = dicing_marker_LB.copy().rotate(np.pi/2)
		dicing_marker_LT = dicing_marker_RB.copy().rotate(np.pi)

		for i in range(grid_dim[0]):

			for j in range(grid_dim[1]):

				origin_shift_x = grid_size_um[0]*i-grid_size_um[0]*grid_dim[0]/2
				origin_shift_y = grid_size_um[1]*j-grid_size_um[1]*grid_dim[1]/2

				cell.add(dicing_marker_LB.copy().translate(origin_shift_x,origin_shift_y))
				cell.add(dicing_marker_LT.copy().translate(origin_shift_x,origin_shift_y+grid_size_um[1]))
				cell.add(dicing_marker_RB.copy().translate(origin_shift_x+grid_size_um[0],origin_shift_y))
				cell.add(dicing_marker_TR.copy().translate(origin_shift_x+grid_size_um[0],origin_shift_y+grid_size_um[1]))



		# add date stamp

		add_date = self.add_date
		add_parameters = self.add_parameters
		date = self.date
		label = self.label

		info_label_text = ''
		if label != None:

			info_label_text += label + '  '

		if add_date:

			if date == None:

				today = datetime.date.today()
				date = today.strftime('%Y-%m-%d')

			info_label_text += date


		if add_parameters:

			if add_date:

				info_label_text += '      '

			info_label_text += str(grid_size[0]) + 'x' + str(grid_size[1]) + 'mm; opt mf = ' + str(write_field) + ' mm'

		if add_date or add_parameters:

			info_label = gdstk.text(info_label_text, global_coord_text_size*2, (-global_alignment_marker_pos_x+250+2*global_coord_text_size ,-global_alignment_marker_pos_y+2*global_coord_text_size), layer=1)
			cell.add(*info_label)



		ref = gdstk.Reference(cell,origin=(global_origin_shift_x,global_origin_shift_y))
		cell_save.add(ref)
		cell_save.flatten()



		# Save the layout
		lib.add(cell_save)
		lib.write_gds(save_location)
