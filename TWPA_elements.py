"""
List of classes in the module:
	- Overlap_jj 
	- Overlap_capa 
	- Pad
	- FeedLine
	- Meander
	- Overlap_LER
	- RHcell
	- LHcell

Note that all the classes store the variables self.x_size_of_cell and self.y_size_of_cell:
1) x_size_of_cell idetifies the x position where the unit cell ends (where the next unit cell will be connected)
2) y_size_of_cell idetifies the distance on the y-axis between the origin and the bottom of the unit cell
"""

import gdstk
import numpy as np
import datetime


class Overlap_jj:
	'''
	Class to generate junctions with overlap technique (shape -|-)
		The variable self.x_size_of_cell and self.y_size_of_cell store the size of the structure for global use
	'''
	def __init__(self):
		
		# self.litho_overlap = 0.01
		# self.spacing_jj = 3.0
		# self.electrode_height_difference = 1.0
		# self.y_low_current_ground = 3.0
		self.litho_overlap = None
		self.height_jj = None
		self.width_jj = None
		self.spacing_jj = None
		self.electrode_height_difference = None
		self.y_low_current_ground = None

		self.jj_bottom_layer = 1
		self.jj_top_layer = 2
		self.jj_ground_layer = 3
		
		self.cells_in_element = 1

	def generateCell(self, **kwargs):

		if 'add_ground' in kwargs:
			add_ground = kwargs.get("add_ground")
		else:
			add_ground = False

		litho_overlap = self.litho_overlap
		spacing = self.spacing_jj
		height = self.height_jj
		width = self.width_jj
		electrode_height_difference = self.electrode_height_difference
		y_low_current_ground = self.y_low_current_ground

		jj_bottom_layer = self.jj_bottom_layer
		jj_top_layer = self.jj_top_layer
		jj_ground_layer = self.jj_ground_layer

		# generate cell to add features to
		cell_out = gdstk.Cell("SingleOverlap")

		x_position = 0
		y_position = 0

		# add bottom layer 
		bottom_electrode = gdstk.rectangle((-litho_overlap/2.0,-(height/2.0+electrode_height_difference)), (spacing/2.0+width,(height/2.0+electrode_height_difference)), layer=jj_bottom_layer)
		cell_out.add(bottom_electrode.copy().translate(x_position,y_position))
		x_position += spacing/2.0

		# add top layer
		top_electrode = gdstk.rectangle((0,-height/2.0), (spacing/2.0+width+litho_overlap/2.0,height/2.0), layer=jj_top_layer)
		cell_out.add(top_electrode.copy().translate(x_position,y_position))
		x_position += spacing/2.0+width

		# add ground
		if add_ground:
			ground = gdstk.rectangle((-litho_overlap/2.0,-(height/2.0+electrode_height_difference+y_low_current_ground)), (spacing+width,(height/2.0+electrode_height_difference+y_low_current_ground)), layer=jj_ground_layer)

			bottom_electrodes =  cell_out.get_polygons(layer=jj_bottom_layer,datatype=0)

			ground_exclusion = gdstk.boolean(ground, bottom_electrodes, 'not',  precision=1e-3, layer=jj_ground_layer)			
			cell_out.add(*ground_exclusion)


		self.x_size_of_cell = x_position 
		self.y_size_of_cell = height/2.0 + electrode_height_difference #respect to origin

		return cell_out


class Overlap_capa:
	### Work in progress ###
	'''
	Class to generate capacitors with overlap technique (shape -|-)
		The variable self.x_size_of_cell and self.y_size_of_cell store the size of the structure for global use
	'''
	def __init__(self):

		# self.litho_overlap = 0.01
		# self.spacing_capa = 3.0
		# self.electrode_height_difference = 1.5
		# self.y_low_current_ground = 3.0
		
		self.litho_overlap = None
		self.height_capa = None
		self.width_capa = None
		self.new_area_capa = None
		self.spacing_capa = None
		self.electrode_height_difference = None
		self.y_low_current_ground = None

		self.capa_bottom_layer = 1
		self.capa_top_layer = 2
		self.capa_ground_layer = 3

		self.cells_in_element = 1

	def generateCell(self, **kwargs):

		if 'add_ground' in kwargs:
			add_ground = kwargs.get("add_ground")
		else:
			add_ground = False
		if 'change_area_capa' in kwargs:
			change_area_capa = kwargs.get("change_area_capa")
		else:
			change_area_capa = False

		litho_overlap = self.litho_overlap
		spacing = self.spacing_capa
		height = self.height_capa
		width = self.width_capa
		new_area_capa = self.new_area_capa
		electrode_height_difference = self.electrode_height_difference
		y_low_current_ground = self.y_low_current_ground

		capa_bottom_layer = self.capa_bottom_layer
		capa_top_layer = self.capa_top_layer
		capa_ground_layer = self.capa_ground_layer

		# generate cell to add features to
		cell_out = gdstk.Cell("SingleOverlap")

		x_position = 0
		y_position = 0

		# add bottom layer 
		bottom_electrode = gdstk.rectangle((-litho_overlap/2,-(height/2+electrode_height_difference)), (spacing/2+width,(height/2+electrode_height_difference)), layer=capa_bottom_layer)
		cell_out.add(bottom_electrode.copy().translate(x_position,y_position))
		x_position += spacing/2

		# add top layer
		if change_area_capa:
			new_width = width+spacing/2
			new_height = (new_area_capa/new_width)
			diff_height_capa = new_height - height
			diff_width = spacing/2
		else:
			diff_height_capa = 0
			diff_width=0
		top_electrode = gdstk.rectangle((-diff_width,-(height+diff_height_capa)/2), (spacing/2+width+litho_overlap/2,(height+diff_height_capa)/2), layer=capa_top_layer)

		cell_out.add(top_electrode.copy().translate(x_position,y_position))
		x_position += spacing/2+width

		# add ground
		if add_ground:
			ground = gdstk.rectangle((0,-(height/2+electrode_height_difference+y_low_current_ground)), (spacing+width,(height/2+electrode_height_difference+y_low_current_ground)), layer=capa_ground_layer)

			bottom_electrodes =  cell_out.get_polygons(layer=capa_bottom_layer,datatype=0)

			ground_exclusion = gdstk.boolean(ground, bottom_electrodes, 'not',  precision=1e-3, layer=capa_ground_layer)			
			cell_out.add(*ground_exclusion)

		self.x_size_of_cell = x_position
		self.y_size_of_cell = height/2+electrode_height_difference #respect to origin

		return cell_out


class Pad():
	'''
	Generate a pad with a narrower arm and a taper connecting the two:
		There are three options:
			1) If CPW is True and Exclude_ground is True it generates only the ground exclusion for CPW geometry
			2) If CPW is False and Exclude_ground is False it generates only the pad without ground
			3) If CPW is True and Exclude_ground is False it generates both the pad and the ground
		The parameter self.x_size_of_Pad stores the length of the pad (plus ground if present)
	'''
	def __init__(self):

		self.CPW = True
		self.Exclude_ground = False

		### Parameters definition
		self.x_pad = 150
		self.y_pad = 300 
		self.taper_length = 50
		self.x_pad_gap = 50
		self.y_pad_gap = 135
		self.x_arm = 20
		self.y_arm = 40
		self.arm_gap = 21

		### Layer definition
		self.pad_layer = 1
		self.arm_layer = 2
		self.ground_layer = 3

	def GeneratePad(self):

		### Create cell
		cell = gdstk.Cell('Pad')

		### Parameters definition
		x_pad = self.x_pad
		y_pad = self.y_pad
		x_arm = self.x_arm
		y_arm = self.y_arm
		taper_length = self.taper_length
		x_pad_gap = self.x_pad_gap
		y_pad_gap = self.y_pad_gap
		arm_gap = self.arm_gap

		### Layer definition
		pad_layer = self.pad_layer
		arm_layer = self.arm_layer
		ground_layer = self.ground_layer

		### Create pad
		points = [  (0,0), (x_pad,0),
					(x_pad + taper_length, y_pad/2 - y_arm/2),
					(x_pad + taper_length, y_pad/2 + y_arm/2),
					(x_pad, y_pad), (0, y_pad) ]

		pad = gdstk.Polygon(points, layer=pad_layer)
		arm = gdstk.rectangle((x_pad + taper_length, y_pad/2 - y_arm/2), (x_pad + taper_length + x_arm, y_pad/2 + y_arm/2), layer=arm_layer)
		
		### Create ground
		if self.CPW:
			points_ground = [  (-x_pad_gap,-y_pad_gap), (x_pad,-y_pad_gap),
						(x_pad + taper_length, y_pad/2 - y_arm/2 - arm_gap),
						(x_pad + taper_length, y_pad/2 + y_arm/2 + arm_gap),
						(x_pad, y_pad + y_pad_gap), (-x_pad_gap, y_pad + y_pad_gap) ]

			pad_ground = gdstk.Polygon(points_ground, layer=ground_layer)
			arm_ground = gdstk.rectangle((x_pad + taper_length, y_pad/2 - y_arm/2 - arm_gap), (x_pad + taper_length + x_arm, y_pad/2 + y_arm/2 + arm_gap), layer=ground_layer)
			if self.Exclude_ground:
				pad_exclusion = gdstk.boolean(pad_ground, pad, 'not',  precision=1e-3, layer=ground_layer)
				arm_exclusion = gdstk.boolean(arm_ground, arm, 'not',  precision=1e-3, layer=ground_layer)

				pad_exclusion[0].translate(x_pad_gap, -y_pad/2)
				arm_exclusion[0].translate(x_pad_gap, -y_pad/2)
				arm_exclusion[1].translate(x_pad_gap, -y_pad/2)
				pad.translate(x_pad_gap, -y_pad/2)
				arm.translate(x_pad_gap, -y_pad/2)

				cell.add(pad, arm, pad_exclusion[0], arm_exclusion[0], arm_exclusion[1])
			else:
				pad_ground.translate(x_pad_gap, -y_pad/2)
				arm_ground.translate(x_pad_gap, -y_pad/2)
				pad.translate(x_pad_gap, -y_pad/2)
				arm.translate(x_pad_gap, -y_pad/2)
				cell.add(pad, arm, pad_ground, arm_ground)

			self.x_size_of_Pad = x_pad + x_pad_gap + taper_length + x_arm
		else:
			### Add only pad
			pad.translate(0, -y_pad/2)
			arm.translate(0, -y_pad/2)
			cell.add(pad, arm)
			self.x_size_of_Pad = x_pad + taper_length + x_arm

		cell.flatten()

		return cell

class Pad_TWPA_inv_microstrip:

	######################################################
	## Pads for TWPAs with inverted microstrip geometry ##
	######################################################

	"""
	Class to generate the pads for the TWPAs with 50 Ohms matching.

	"""
	def __init__(self):

		# These parameters are default parameters optimized by SW for 50 nm of Al2O3 deposited with ALD for the top ground

		self.bonding_pad_width  = 100 # Do not change
		self.bonding_pad_length = 280 # Do not change
		self.bonding_pad_gap_x    = 10 # Do not change
		self.bonding_pad_gap_y    = 15 # Do not change
        
		self.connecting_line_length = 600 # You can change to adapt to the length of your TWPA
		self.connecting_line_width  = 4 # Do not change
		self.connecting_wire_gap    = 13 # Do not change
		self.pad_wire_overlap       = 2 # You can change but not a relevant parameter
        
		self.capacitance_along_connecting_wire_width       = 2 # Do not change
		self.capacitance_along_connecting_wire_pitch_first = 90 # Do not change
		self.capacitance_along_connecting_wire_pitch       = 100 # Do not change

		self.x_dice_gap = 50
        
        ## Layer index
		self.layer_1      = 1
		self.layer_2      = 2
		self.layer_ground = 3
		self.layer_shift  = 0
		
	def Generate_Pad_TWPA(self):

		cell = gdstk.Cell('pad_inv')
		
		bonding_pad_width = self.bonding_pad_width
		bonding_pad_length = self.bonding_pad_length
		bonding_pad_gap_x = self.bonding_pad_gap_x
		bonding_pad_gap_y = self.bonding_pad_gap_y
		
		connecting_line_length = self.connecting_line_length
		connecting_line_width = self.connecting_line_width
		connecting_wire_gap = self.connecting_wire_gap
		pad_wire_overlap = self.pad_wire_overlap
		
		capacitance_along_connecting_wire_width = self.capacitance_along_connecting_wire_width
		capacitance_along_connecting_wire_pitch_first = self.capacitance_along_connecting_wire_pitch_first
		capacitance_along_connecting_wire_pitch = self.capacitance_along_connecting_wire_pitch
		
		x_dice_gap = self.x_dice_gap

		layer_shift = self.layer_shift
		pad_layer = layer_shift + self.layer_1
		connecting_wire_layer = layer_shift + self.layer_2
		ground_layer = layer_shift + self.layer_ground

		x_len = x_dice_gap
		y_len_top = 0
		y_len_bottom = 0

		## Generate cells to add features to

		bonding_pad = gdstk.rectangle((x_dice_gap,-bonding_pad_width/2.0), (bonding_pad_length + x_dice_gap,bonding_pad_width/2.0), layer=pad_layer)
		cell.add(bonding_pad.copy().translate(0,0))

		x_len += bonding_pad_length
		y_len_top += bonding_pad_width/2.0
		y_len_bottom += bonding_pad_width/2.0
		
		connecting_wire = gdstk.rectangle((-pad_wire_overlap + x_dice_gap,-connecting_line_width/2.0), (connecting_line_length + x_dice_gap,connecting_line_width/2.0), layer=connecting_wire_layer)
		cell.add(connecting_wire.copy().translate(bonding_pad_length,0))

		x_len += connecting_line_length

		
		top_ground_pad_window = gdstk.rectangle((0,-bonding_pad_width/2.0-bonding_pad_gap_y), (bonding_pad_length+bonding_pad_gap_x+x_dice_gap,bonding_pad_width/2.0+bonding_pad_gap_y), layer=ground_layer)
		cell.add(top_ground_pad_window.copy().translate(0,0))

		y_len_top += bonding_pad_gap_y
		y_len_bottom += bonding_pad_gap_y
		
		top_ground_connecting_wire_window = gdstk.rectangle((x_dice_gap,-connecting_line_width/2.0-connecting_wire_gap), (connecting_line_length - bonding_pad_gap_x + x_dice_gap,connecting_line_width/2.0+connecting_wire_gap), layer=ground_layer)

		top_ground_wire_for_capa_along_connecting_wire = gdstk.rectangle((x_dice_gap,-connecting_line_width/2.0-connecting_wire_gap-1), (capacitance_along_connecting_wire_width + x_dice_gap,connecting_line_width/2.0+connecting_wire_gap+1), layer=ground_layer)
		
		top_ground_connecting_wire_window = gdstk.boolean(top_ground_connecting_wire_window,top_ground_wire_for_capa_along_connecting_wire.copy(),'not',layer=ground_layer)

		for i in range(int(capacitance_along_connecting_wire_pitch_first),int(connecting_line_length),int(capacitance_along_connecting_wire_pitch)):
			
			top_ground_connecting_wire_window = gdstk.boolean(top_ground_connecting_wire_window,top_ground_wire_for_capa_along_connecting_wire.copy().translate(i,0),'not',layer=ground_layer)
			
		for i in range(0,len(top_ground_connecting_wire_window)):
			
			cell.add(top_ground_connecting_wire_window[i].copy().translate(bonding_pad_length+bonding_pad_gap_x,0))
			
		cell.flatten()

		self.x_size_of_Pad_inv = x_len

		return cell

class Pad_simple:

	########################
	## Simple bonding pad ##
	########################

	"""
	Class to generate a bonding pad with connecting wire.

	"""

	def __init__(self):

		self.bonding_pad_width  = 100
		self.bonding_pad_length = 280
        
		self.connecting_line_length = 400
		self.connecting_line_width  = 4
		self.pad_wire_overlap       = 2
        
        ## Layer index
		self.layer_1      = 1
		self.layer_2      = 2
		self.layer_shift  = 0
	
	def Generate_Pad(self):

		bonding_pad_width = self.bonding_pad_width
		bonding_pad_length = self.bonding_pad_length
        
		connecting_line_length = self.connecting_line_length
		connecting_line_width = self.connecting_line_width
		pad_wire_overlap = self.pad_wire_overlap
        
		layer_shift = self.layer_shift
		pad_layer = layer_shift + self.layer_1
		connecting_wire_layer = layer_shift + self.layer_2

        ## Generate cell to add features to
		cell = gdstk.Cell('pad')

		x_len = 0

		bonding_pad = gdstk.rectangle((0,-bonding_pad_width/2.0), (bonding_pad_length,bonding_pad_width/2.0), layer=pad_layer)

		cell.add(bonding_pad.copy().translate(0,0))

		x_len += bonding_pad_length
        
		connecting_wire = gdstk.rectangle((-pad_wire_overlap,-connecting_line_width/2.0), (connecting_line_length,connecting_line_width/2.0), layer=connecting_wire_layer)
		
		cell.add(connecting_wire.copy().translate(bonding_pad_length,0))

		x_len += connecting_line_length

		cell.flatten()
		
		self.x_size_of_Pad_square = x_len

		return cell
	

class FeedLine():
	'''
	Class to generate a feedline with tapered pads using the Pad class:
		There are two options:
			1) If CPW is True it generates only the ground exclusion for CPW geometry
			2) If CPW is False it generates only the feedline without ground
	'''
	def __init__(self):

		self.CPW = True
		self.Exclude_ground = True

		### Parameters definition
		self.x_pad = 150
		self.y_pad = 300
		self.x_arm = 20
		self.y_arm = 50
		self.taper_length = 150
		self.x_pad_gap = 35
		self.y_pad_gap = 175
		self.arm_gap = 30

		self.feedline_length = 8000
		self.feedline_width = 50
		self.feedline_gap = 30

		### Layer definition
		self.feedline_layer = 1
		self.ground_layer = 2

	def GenerateFeedline(self):

		### Create cell
		cell = gdstk.Cell('Feedline')

		### Layer definition
		feedline_layer = self.feedline_layer
		ground_layer = self.ground_layer

		### Generate left tapered pad
		Pad_inst = Pad()
		Pad_inst.x_pad = self.x_pad
		Pad_inst.y_pad = self.y_pad
		Pad_inst.x_arm = self.x_arm
		Pad_inst.y_arm = self.y_arm
		Pad_inst.taper_length = self.taper_length
		Pad_inst.x_pad_gap = self.x_pad_gap
		Pad_inst.y_pad_gap = self.y_pad_gap
		Pad_inst.arm_gap = self.arm_gap
		Pad_inst.pad_layer = feedline_layer
		Pad_inst.arm_layer = feedline_layer
		Pad_inst.ground_layer = ground_layer
		Pad_inst.CPW = self.CPW
		Pad_inst.Exclude_ground = self.Exclude_ground

		pad = Pad_inst.GeneratePad()

		pad_left = gdstk.Reference(pad, origin=(0,0), rotation=0)

		cell.add(pad_left)

		### Generate feedline
		feedline_length = self.feedline_length - 2.0*Pad_inst.x_size_of_Pad
		feedline_width = self.feedline_width
		feedline_gap = self.feedline_gap

		feed_line = gdstk.rectangle((0,-feedline_width/2.0),(feedline_length,+feedline_width/2.0), layer=feedline_layer)

		if self.CPW:
			feed_line_ground = gdstk.rectangle((0,-feedline_width/2.0-feedline_gap),(feedline_length,feedline_width/2.0+feedline_gap), layer=ground_layer)
			feed_line_exclusion = gdstk.boolean(feed_line_ground, feed_line, 'not',  precision=1e-3, layer=ground_layer)
			feed_line_exclusion[0].translate(Pad_inst.x_size_of_Pad,0)
			feed_line_exclusion[1].translate(Pad_inst.x_size_of_Pad,0)

			cell.add(feed_line_exclusion[0], feed_line_exclusion[1])
			
		feed_line.translate(Pad_inst.x_size_of_Pad,0)
		cell.add(feed_line)

		### Generate right tapered pad
		pad_right = gdstk.Reference(pad, origin=(feedline_length+2.0*Pad_inst.x_size_of_Pad,0), rotation=np.pi)

		cell.add(pad_right)

		cell.flatten()

		return cell


class Meander() :
	'''
	Class to generate a meader:
		The parameter self.x_size_of_meander stores the size of the meander along the x direction
	'''
	def __init__(self):

		### Parameters definition
		self.width_of_wire = 10
		self.spacing_between_steps = 25
		self.length_of_step = 75
		self.length_of_coupling_step = 150
		self.length_of_meander = 1100

		### Layer definition
		self.meander_layer = 1

	def GenerateMeander(self):

		### Create cell
		cell = gdstk.Cell('Meander')

		### Parameters definition
		width_of_wire = self.width_of_wire
		spacing_between_steps = self.spacing_between_steps
		length_of_step = self.length_of_step
		length_of_coupling_step = self.length_of_coupling_step
		length_of_meander = self.length_of_meander

		### Layer definition
		meander_layer = self.meander_layer

		### Creating the meander
		bend_radius = (spacing_between_steps + width_of_wire) / 2

		meander = gdstk.FlexPath((0, width_of_wire/2), width_of_wire, layer=meander_layer)

		meander.commands(	"h", length_of_coupling_step,
							"a", bend_radius, -np.pi)

		length_of_meander_tmp = length_of_coupling_step + np.pi * bend_radius

		endpoint_y = 0

		i = 0
		while length_of_meander_tmp < length_of_meander:

			if (i%2) == 0:
				sign = -1
			else:
				sign = 1

			if (length_of_meander - length_of_meander_tmp) <= (length_of_step + np.pi * bend_radius):
				meander.commands("h", sign * (length_of_meander - length_of_meander_tmp))

				if (i%2) == 0:
					endpoint_x = length_of_coupling_step - (length_of_meander - length_of_meander_tmp)
				else:
					endpoint_x = length_of_meander - length_of_meander_tmp

				length_of_meander_tmp += (length_of_meander - length_of_meander_tmp)
			else:
				meander.commands(	"h", sign * length_of_step,
									"a", bend_radius, -sign * np.pi)
				length_of_meander_tmp += length_of_step + np.pi * bend_radius

			endpoint_y -= spacing_between_steps + width_of_wire
			i += 1

		meander.to_polygons()
		meander.translate(0, -width_of_wire)
		endpoint_y -= width_of_wire
		endpoint = np.array([endpoint_x, endpoint_y])

		### Add meander to cell
		cell.add(meander)

		### Update endpoints
		self.endpoints = (np.array([0,0]), np.array(endpoint))  # The origin is at the top of the meander
																# while endpoint is the bottom of the meander

		self.x_size_of_meander = bend_radius + length_of_coupling_step + width_of_wire/2.0

		return cell


class Overlap_LER():
	'''
	Class for generation of a lumped element resonator
		which is composed by three structures
			1) A meander generated by the class Meander
			2) A capacitor generated by the class SinglePPC, it is possible to add a chain of capacitors changing the parameter "number_of_capacitors"
			3) Two patches generated by the class SinglePatch to connect the capacitor(s) with the meander
	There are two options:
		If CPW is True it makes the ground plane exclusion for CPW geometry
		If CPW is False it generates only the meander and the capacitor(s)
	'''
	def __init__(self):

		### Parameters definition
		self.CPW = True

		self.litho_overlap = 0.1

		### Meander 
		self.resonators_ground_gap = 50
		self.width_of_wire = 10
		self.spacing_between_steps = 25
		self.length_of_step = 75
		self.length_of_coupling_step = 150
		self.length_of_meander = 2925

		### Capacitor
		self.area_capa = None
		self.spacing_capa = 10.0
		self.number_of_capacitors = 2
		self.electrode_height_difference = 2.5

		### Layer definition
		self.bottom_layer = 101
		self.capa_top_layer = 2
		self.meander_layer = 3
		self.ground_layer = 4
		self.ground_layer_low_current = 5

		self.cells_in_element = 1

	def generateCell(self, **kwargs):

		if 'reflection' in kwargs:
			reflection = kwargs.get("reflection")
		else:
			reflection = False

		### Create cell
		cell = gdstk.Cell("Lumped element resonator")
		cell_capa = gdstk.Cell("Capacitor")

		litho_overlap = self.litho_overlap

		### Generate meander inductor
		Meander_inst = Meander()
		Meander_inst.width_of_wire = self.width_of_wire
		Meander_inst.spacing_between_steps = self.spacing_between_steps
		Meander_inst.length_of_step = self.length_of_step
		Meander_inst.length_of_coupling_step = self.length_of_coupling_step
		Meander_inst.length_of_meander = self.length_of_meander
		Meander_inst.meander_layer = self.bottom_layer

		meander = Meander_inst.GenerateMeander()

		### Generate PPC
		PPC_inst = Overlap_capa()

		PPC_inst.litho_overlap = self.litho_overlap

		number_of_capacitors = self.number_of_capacitors
		PPC_inst.spacing_capa= self.spacing_capa
		PPC_inst.electrode_height_difference = self.electrode_height_difference
		PPC_inst.height_capa = Meander_inst.width_of_wire - 2.0*PPC_inst.electrode_height_difference
		PPC_inst.width_capa = self.area_capa/PPC_inst.height_capa
		PPC_inst.capa_bottom_layer = self.bottom_layer
		PPC_inst.capa_top_layer = self.capa_top_layer

		PPC = PPC_inst.generateCell()

		### Generate capacitor to meander connection
		# connection_length = Meander_inst.endpoints[1][0] - number_of_capacitors*PPC_inst.x_size_of_cell/2.0 - litho_overlap/2.0
		connection_length = Meander_inst.endpoints[1][0] - number_of_capacitors*PPC_inst.x_size_of_cell/2.0 + PPC_inst.width_capa + PPC_inst.spacing_capa/2.0
		connection = gdstk.rectangle((0,-(Meander_inst.width_of_wire)/2.0), (connection_length,(Meander_inst.width_of_wire)/2.0), layer=Meander_inst.meander_layer)

		### Add connection
		connection_right = connection.copy().translate(number_of_capacitors*PPC_inst.x_size_of_cell/2.0-PPC_inst.width_capa-PPC_inst.spacing_capa/2.0,Meander_inst.endpoints[1][1]+Meander_inst.width_of_wire/2.0)
		connection_left = connection.copy().rotate(np.pi).translate(-number_of_capacitors*PPC_inst.x_size_of_cell/2.0+PPC_inst.width_capa+PPC_inst.spacing_capa/2.0,Meander_inst.endpoints[1][1]+Meander_inst.width_of_wire/2.0)
		cell.add(connection_right, connection_left)

		### Add capacitor(s)
		for i in range(number_of_capacitors):
			if i % 2 == 0:
				ref = gdstk.Reference(PPC, origin=(i*PPC_inst.x_size_of_cell , 0), rotation=0)
			else:
				ref = gdstk.Reference(PPC, origin=((i+1)*PPC_inst.x_size_of_cell, 0), rotation=np.pi)
			cell_capa.add(ref)

		PPC_ref = gdstk.Reference(cell_capa, origin=(-number_of_capacitors*(PPC_inst.x_size_of_cell)/2.0, Meander_inst.endpoints[1][1]+Meander_inst.width_of_wire/2.0))
		cell.add(PPC_ref)


		### Add meander and ground
		if self.CPW:
			ground_layer = self.ground_layer
			resonators_ground_gap = self.resonators_ground_gap
			rectangle = gdstk.rectangle((-Meander_inst.x_size_of_meander-resonators_ground_gap,resonators_ground_gap), (Meander_inst.x_size_of_meander+resonators_ground_gap, Meander_inst.endpoints[1][1]-resonators_ground_gap), layer=ground_layer)
			rectangle.fillet(resonators_ground_gap)
			Meander_ref = gdstk.Reference(meander, origin=(0,0))
			ground_exclusion = gdstk.boolean(rectangle, Meander_ref, 'not',  precision=1e-3, layer=ground_layer)
			Meander_ref = gdstk.Reference(meander, origin=(0,0), x_reflection=True, rotation=np.pi)
			ground_exclusion = gdstk.boolean(ground_exclusion, Meander_ref, 'not',  precision=1e-3, layer=ground_layer)
			ground_exclusion = gdstk.boolean(ground_exclusion, connection_right, 'not',  precision=1e-3, layer=ground_layer)
			ground_exclusion = gdstk.boolean(ground_exclusion, connection_left, 'not',  precision=1e-3, layer=ground_layer)			
			cell.add(ground_exclusion[0])
			self.x_size_of_cell = 2.0*(Meander_inst.x_size_of_meander+resonators_ground_gap)
			self.y_size_of_cell = Meander_inst.endpoints[1][1] + 2.0*resonators_ground_gap
		else:
			self.x_size_of_cell = 2.0*Meander_inst.x_size_of_meander
			self.y_size_of_cell = Meander_inst.endpoints[1][1]
		Meander_ref = gdstk.Reference(meander, origin=(0,0))
		cell.add(Meander_ref)
		Meander_ref = gdstk.Reference(meander, origin=(0,0), x_reflection=True, rotation=np.pi)
		cell.add(Meander_ref)
		cell.flatten()

		return cell


class RHcell:
	'''
	Class to generate the unit cell for a Right-Handed Josephson Transmission Line
	  There is one function:
		- generateCell: generate the unit cell of RHJTL with two capacitors connected to a chain of junction using the classes Overlap_jj and Overlap_capa
		The variable self.x_size_of_cell and self.y_size_of_cell store sizes of the structure for global use
		Note that it stores the variables self.x_size_of_cell and self.y_size_of_cell of the classes Overlap_jj and Overlap_capa in the
		variables:
		1) x_size_of_jj
		2) y_size_of_jj
		3) x_size_of_capa
		4) y_size_of_capa
	'''

	def __init__(self):

		# self.litho_overlap = 0.1
		# self.etching_offset = 0.25
		# self.spacing_jj = 2.0
		# self.electrode_height_difference_jj = 1.0
		# self.number_of_junctions = 2
		# self.spacing_capa = 2.0
		# self.electrode_height_difference_capa = 1.5
		# self.number_of_capacitors = 2

		self.litho_overlap = None
		self.etching_offset = None

		self.width_jj = None
		self.height_jj = None
		self.spacing_jj = None
		self.electrode_height_difference_jj = None
		self.number_of_junctions = None

		self.area_capa = None
		self.new_area_capa = None
		self.spacing_capa = None
		self.electrode_height_difference_capa = None
		self.number_of_capacitors = None

		self.jj_bottom_layer = 1
		self.capa_bottom_layer = 2
		self.jj_top_layer = 3
		self.capa_top_layer = 4
		self.ground_layer = 5

		self.cells_in_element = 1


	def generateCell(self, **kwargs):

		if 'change_area_capa' in kwargs:
			change_area_capa = kwargs.get("change_area_capa")
		else:
			change_area_capa = False

		PPC_inst = Overlap_capa()
		PPC_inst.litho_overlap = self.litho_overlap
		PPC_inst.height_capa = self.spacing_jj + 2*self.width_jj -2*self.electrode_height_difference_capa
		PPC_inst.new_area_capa = self.new_area_capa
		PPC_inst.spacing_capa = self.spacing_capa
		PPC_inst.electrode_height_difference = self.electrode_height_difference_capa
		PPC_inst.capa_top_layer = self.capa_top_layer
		PPC_inst.capa_ground_layer = self.ground_layer
		PPC_inst.width_capa = self.area_capa/PPC_inst.height_capa + self.etching_offset
		PPC_inst.capa_bottom_layer = 101
		PPC_to_ground = PPC_inst.generateCell(change_area_capa=change_area_capa)
		PPC_inst.width_capa = self.area_capa/PPC_inst.height_capa
		PPC_inst.capa_bottom_layer = self.capa_bottom_layer
		PPC_inst.y_low_current_ground = self.y_low_current_ground
		self.PPC = PPC_inst.generateCell(change_area_capa=change_area_capa)

		JJ_inst = Overlap_jj()
		JJ_inst.litho_overlap = self.litho_overlap
		JJ_inst.etching_offset = self.etching_offset
		JJ_inst.y_low_current_ground = self.y_low_current_ground
		JJ_inst.height_jj = self.height_jj
		JJ_inst.width_jj = self.width_jj
		JJ_inst.spacing_jj = self.spacing_jj
		JJ_inst.electrode_height_difference = self.electrode_height_difference_jj
		JJ_inst.jj_bottom_layer = self.jj_bottom_layer
		JJ_inst.jj_top_layer = self.jj_top_layer
		JJ_inst.jj_ground_layer = self.ground_layer
		self.JJ = JJ_inst.generateCell()

		litho_overlap = self.litho_overlap 
		ground_layer = self.ground_layer
		number_of_capacitors = self.number_of_capacitors
		number_of_junctions = self.number_of_junctions
		etching_offset = self.etching_offset


		# generate cell to add features to
		cell_out = gdstk.Cell("RHcell")

		# add JJ
		x_pos = 0
		y_pos = 0
		x_increment = JJ_inst.x_size_of_cell
		for i in range(number_of_junctions):
			if i%2 == 0:
				JJ_ref = gdstk.Reference(self.JJ, origin=(x_pos+i*x_increment,y_pos), rotation=0)
			else:
				JJ_ref = gdstk.Reference(self.JJ, origin=(x_pos+(i+1)*x_increment,y_pos), rotation=np.pi)
			cell_out.add(JJ_ref)

		# add chain of junctions
		x_pos += (i+1)*x_increment
		y_pos += JJ_inst.y_size_of_cell
		y_increment = PPC_inst.x_size_of_cell

		x_increment = PPC_inst.y_size_of_cell

		for i in range(number_of_capacitors):
			if i%2 == 0:
				PPC_ref_top = gdstk.Reference(self.PPC, origin=(x_pos,y_pos), rotation=np.pi/2)
				PPC_ref_bottom = gdstk.Reference(self.PPC, origin=(x_pos,-y_pos), rotation=-np.pi/2)
			else:
				PPC_ref_top = gdstk.Reference(PPC_to_ground, origin=(x_pos,y_pos+(i+1)*(y_increment+etching_offset/2)), rotation=-np.pi/2)
				PPC_ref_bottom = gdstk.Reference(PPC_to_ground, origin=(x_pos,-y_pos-(i+1)*(y_increment+etching_offset/2)), rotation=np.pi/2)
			cell_out.add(PPC_ref_bottom, PPC_ref_top)

		y_pos += number_of_capacitors*y_increment 
		x_pos_tot = x_pos + x_increment

		# add ground
		y_ground = JJ_inst.y_size_of_cell+PPC_inst.x_size_of_cell+PPC_inst.spacing_capa/2
		x_ground = x_pos
		ground = gdstk.rectangle((-litho_overlap/2,-y_ground), (x_pos+litho_overlap/2,y_ground), layer=ground_layer)
		ground.translate(JJ_inst.x_size_of_cell,0)
		cell_out.add(ground)

		cell_out.flatten()

		self.x_size_of_capa = PPC_inst.x_size_of_cell
		self.y_size_of_capa = PPC_inst.y_size_of_cell
		self.x_size_of_jj = JJ_inst.x_size_of_cell
		self.y_size_of_jj = JJ_inst.y_size_of_cell
		self.x_size_of_cell = x_pos
		self.x_size_of_cell_tot = x_pos_tot
		self.y_size_of_cell = y_pos

		return cell_out
	

class Overlap_SNAIL:

	'''
	Class to generate a SNAIL with overlap junctions technique (shape -|-)
		The variable self.x_size_of_cell and self.y_size_of_cell store the size of the structure for global use
	'''

	def __init__(self):

		self.litho_overlap = None
		self.etching_offset = None

		self.area_ratio = None


		self.width_jj_large = None
		self.height_jj_large = None
		self.spacing_jj_large = None
		self.electrode_height_difference_jj = None
		self.number_of_large_junctions = None
		
		self.width_jj_small = None
		self.height_jj_small = None

		self.loop_height = None
		self.loop_width = None
		self.loop_arm_width = None

		self.ground_capacitance_pads_height = None
		self.ground_capacitance_pads_width = None

		self.invert_SNAIL = None

		self.pads = None

		self.jj_bottom_layer = 1
		self.jj_top_layer = 3

		self.small_jj_top_layer = 2

		self.cells_in_element = 1


	def generateCell(self, **kwargs):

		JJ_inst = Overlap_jj()
		JJ_inst.litho_overlap = self.litho_overlap
		JJ_inst.etching_offset = self.etching_offset
		JJ_inst.height_jj = self.height_jj_large
		JJ_inst.width_jj = self.width_jj_large
		JJ_inst.spacing_jj = self.spacing_jj_large
		JJ_inst.electrode_height_difference = self.electrode_height_difference_jj
		JJ_inst.jj_bottom_layer = self.jj_bottom_layer
		JJ_inst.jj_top_layer = self.jj_top_layer
		self.JJ_large = JJ_inst.generateCell()

		height_jj_large = self.height_jj_large
		width_jj_large = self.width_jj_large
		spacing_jj_large = self.spacing_jj_large

		height_jj_small = self.height_jj_small
		width_jj_small = self.width_jj_small

		electrode_height_difference_jj = self.electrode_height_difference_jj

		ground_capacitance_pads_height = self.ground_capacitance_pads_height
		ground_capacitance_pads_width = self.ground_capacitance_pads_width

		litho_overlap = self.litho_overlap 
		number_of_large_junctions = self.number_of_large_junctions
		etching_offset = self.etching_offset

		loop_height = self.loop_height
		loop_width = self.loop_width
		loop_arm_width = self.loop_arm_width


		# generate cell to add features to
		cell_out = gdstk.Cell("SNAILcell")

		# Computing total height of the structure to center the SNAIL chain

		total_height = 2*ground_capacitance_pads_height + loop_height + height_jj_large + 4*electrode_height_difference_jj + height_jj_small
		self.y_offset = total_height/2 - (ground_capacitance_pads_height + height_jj_large + 2*electrode_height_difference_jj + loop_height/2)
		# add left loop arm
		x_pos = 0
		y_pos = total_height/2 - (ground_capacitance_pads_height + height_jj_large + 2*electrode_height_difference_jj + loop_height/2)
		left_arm = gdstk.rectangle((x_pos - litho_overlap/2 ,y_pos + (-loop_height/2 - litho_overlap)), (loop_arm_width,y_pos + (loop_height/2 + litho_overlap)), layer=self.jj_bottom_layer)

		cell_out.add(left_arm.copy().translate(0,0))

		# add large JJs
		y_pos_high = y_pos + loop_height/2 + height_jj_large/2  + electrode_height_difference_jj
		x_increment_large = JJ_inst.x_size_of_cell

		self.x_size_of_large_JJ = JJ_inst.x_size_of_cell
		self.y_size_of_large_JJ = JJ_inst.y_size_of_cell

		for i in range(number_of_large_junctions):
			if i%2 == 0:
				JJ_ref = gdstk.Reference(self.JJ_large, origin=(x_pos+i*x_increment_large,y_pos_high), rotation=0)
			else:
				JJ_ref = gdstk.Reference(self.JJ_large, origin=(x_pos+(i+1)*x_increment_large,y_pos_high), rotation=np.pi)
			cell_out.add(JJ_ref)

		height_large_JJ_cell = JJ_inst.y_size_of_cell

		x_pos += (i+1)*x_increment_large

		# add bootom loop arm left
		x_pos_low = 0
		y_pos_low = y_pos - loop_height/2 - height_jj_small - 2*electrode_height_difference_jj
		bottom_arm_1 = gdstk.rectangle((x_pos_low - litho_overlap/2,y_pos_low), (x_pos_low + loop_width/2 - width_jj_small/2 - spacing_jj_large/2 + litho_overlap/2 + spacing_jj_large/4,(y_pos_low+ height_jj_small + 2*electrode_height_difference_jj)), layer=self.jj_bottom_layer)
		cell_out.add(bottom_arm_1.copy().translate(0,0))


		# add small JJs

		JJ_inst.height_jj = height_jj_small
		JJ_inst.width_jj = width_jj_small
		JJ_inst.jj_bottom_layer = self.jj_bottom_layer
		JJ_inst.jj_top_layer = self.small_jj_top_layer
		self.JJ_small = JJ_inst.generateCell()


		x_pos_low += loop_width/2 - width_jj_small/2 - spacing_jj_large/2 + spacing_jj_large/4
		# x_pos_low += loop_width/2

		y_pos_low += height_jj_small/2 + electrode_height_difference_jj

		x_increment_small = JJ_inst.x_size_of_cell

		self.x_size_of_small_JJ = JJ_inst.x_size_of_cell
		self.y_size_of_small_JJ = JJ_inst.y_size_of_cell

		for i in range(1):
			if i%2 == 0:
				JJ_ref = gdstk.Reference(self.JJ_small, origin=(x_pos_low+i*x_increment_small,y_pos_low), rotation=0)
			else:
				JJ_ref = gdstk.Reference(self.JJ_small, origin=(x_pos_low+(i+1)*x_increment_small,y_pos_low), rotation=np.pi)
			cell_out.add(JJ_ref)

		height_small_JJ_cell = JJ_inst.y_size_of_cell

		# add bootom loop arm right
		x_pos_low += (i+1)*x_increment_small
		y_pos_low += height_jj_small/2 + spacing_jj_large/2

		bottom_arm_2 = gdstk.rectangle((x_pos_low - litho_overlap/2,y_pos_low- height_jj_small - 2*electrode_height_difference_jj), (x_pos_low + loop_width/2 - width_jj_small/2 - spacing_jj_large/2 + litho_overlap/2 + spacing_jj_large/4,(y_pos_low)), layer=self.jj_top_layer)
		cell_out.add(bottom_arm_2.copy().translate(0,0))

		# add right loop arm
		x_pos_low += loop_width/2 - width_jj_small/2 - spacing_jj_large/2 + spacing_jj_large/4 - loop_arm_width
		y_pos_low_up = y_pos_low - litho_overlap
		
		# right_arm = gdstk.rectangle((x_pos_low - litho_overlap/2,(y_pos_low_up)), (x_pos_low + loop_arm_width + litho_overlap/2,(y_pos_low_up + loop_height + height_jj_large  + electrode_height_difference_jj + litho_overlap)), layer=self.jj_top_layer)
		right_arm = gdstk.rectangle((x_pos_low,(y_pos_low_up)), (x_pos_low + loop_arm_width + litho_overlap/2,(y_pos_low_up + loop_height + height_jj_large  + electrode_height_difference_jj + litho_overlap)), layer=self.jj_top_layer)

		cell_out.add(right_arm.copy().translate(0,0))

		# Patch recatngle to compensate for a litho_overlap/2 missing (on purpose) between right arm of the loop and end of the large JJ structure.
		# This is done to avoid a dependence of the loop height on litho_overlap (the loop_height is calculated automatically to maintain a constant area)

		right_arm_upper_patch = gdstk.rectangle((x_pos - litho_overlap/2,(y_pos_high - height_jj_large/2)), (x_pos,(y_pos_high - height_jj_large/2 + height_jj_large)), layer=self.jj_top_layer)
		cell_out.add(right_arm_upper_patch.copy().translate(0,0))

		# Adding the pads for increasing capacitance to ground
		
		if self.pads != False:
		
			x_pos_pad_up = x_pos + loop_arm_width - ground_capacitance_pads_width 
			y_pos_pad_up = y_pos + loop_height/2 + height_jj_large + electrode_height_difference_jj - litho_overlap

			pad_up = gdstk.rectangle((x_pos_pad_up,y_pos_pad_up), (x_pos_pad_up + ground_capacitance_pads_width + litho_overlap/2,(y_pos_pad_up + ground_capacitance_pads_height + litho_overlap + electrode_height_difference_jj)), layer=self.jj_top_layer)

			pad_up_2 = gdstk.rectangle((-litho_overlap/2,y_pos_pad_up + electrode_height_difference_jj), (ground_capacitance_pads_width,(y_pos_pad_up + electrode_height_difference_jj + ground_capacitance_pads_height + litho_overlap)), layer=self.jj_bottom_layer)

			cell_out.add(pad_up.copy().translate(0,0))

			cell_out.add(pad_up_2.copy().translate(0,0))

			x_pos_pad_down = x_pos + loop_arm_width - ground_capacitance_pads_width  
			y_pos_pad_down = y_pos_low + litho_overlap - height_jj_small - 2*electrode_height_difference_jj

			pad_down = gdstk.rectangle((x_pos_pad_down,y_pos_pad_down), (x_pos_pad_down + ground_capacitance_pads_width + litho_overlap/2,(y_pos_pad_down - ground_capacitance_pads_height - litho_overlap)), layer=self.jj_top_layer)

			pad_down_2 = gdstk.rectangle((-litho_overlap/2,y_pos_pad_down), (ground_capacitance_pads_width,(y_pos_pad_down - ground_capacitance_pads_height - litho_overlap)), layer=self.jj_bottom_layer)

			cell_out.add(pad_down.copy().translate(0,0))

			cell_out.add(pad_down_2.copy().translate(0,0))

			self.y_size_of_cell = total_height - 2*ground_capacitance_pads_height

		else:
			
			self.y_size_of_cell = total_height

				
		cell_out.flatten()

		self.x_size_of_cell = x_pos + loop_arm_width 
		

		return cell_out
	

class SNAILcell:

	'''
	Class to generate the unit cell for a SNAIL Transmission Line
	  There is one function:
		- generateCell: generate the unit cell of SNAIL TL, made of 2 SNAIL with three large junctions in one arm and one smaller junction in the other arm using the class Overlap_SNAIL, itself using Overlap_jj
		The variable self.x_size_of_cell and self.y_size_of_cell store sizes of the structure for global use
		Note that it stores the variables self.x_size_of_cell and self.y_size_of_cell of the classes Overlap_jj in the
		variables:
		1) x_size_of_jj
		2) y_size_of_jj
	'''

	def __init__(self):

		self.litho_overlap = None
		self.etching_offset = None

		self.area_ratio = None


		self.width_jj_large = None
		self.height_jj_large = None
		self.spacing_jj_large = None
		self.electrode_height_difference_jj = None
		self.number_of_large_junctions = None
		
		self.width_jj_small = None
		self.height_jj_small = None

		self.loop_height = None
		self.loop_width = None
		self.loop_arm_width = None

		self.ground_capacitance_pads_height = None
		self.ground_capacitance_pads_width = None

		self.invert_SNAIL = False

		self.modulation = 'False'

		self.modulate_capa_only = 'False'

		self.keep_Z_constant_with_modulation = 'False'
		
		self.pads = None

		self.jj_bottom_layer = 1
		self.jj_top_layer = 3

		self.small_jj_top_layer = 2

		self.cells_in_element = 2
		

	def generateCell(self, **kwargs):

		if self.modulation == 'True':

			self.height_jj_large_arr = self.height_jj_large
			self.height_jj_small_arr = self.height_jj_small
			self.ground_capacitance_pads_height_arr = self.ground_capacitance_pads_height

		else:
			self.height_jj_large_arr = np.ones(int(self.cells_in_element))*self.height_jj_large
			self.height_jj_small_arr = np.ones(int(self.cells_in_element))*self.height_jj_small
			self.ground_capacitance_pads_height_arr = np.ones(int(self.cells_in_element))*self.ground_capacitance_pads_height

		SNAIL_inst = Overlap_SNAIL()
		SNAIL_inst.litho_overlap = self.litho_overlap
		SNAIL_inst.etching_offset = self.etching_offset
		SNAIL_inst.width_jj_large = self.width_jj_large
		SNAIL_inst.height_jj_large = self.height_jj_large_arr[0]
		SNAIL_inst.spacing_jj_large = self.spacing_jj_large
		SNAIL_inst.electrode_height_difference_jj = self.electrode_height_difference_jj
		SNAIL_inst.width_jj_small = self.width_jj_small
		SNAIL_inst.height_jj_small = self.height_jj_small_arr[0]
		SNAIL_inst.loop_height = self.loop_height
		SNAIL_inst.loop_width = self.loop_width
		SNAIL_inst.loop_arm_width = self.loop_arm_width
		SNAIL_inst.ground_capacitance_pads_height = self.ground_capacitance_pads_height_arr[0]
		SNAIL_inst.ground_capacitance_pads_width = self.ground_capacitance_pads_width
		SNAIL_inst.number_of_large_junctions = self.number_of_large_junctions
		SNAIL_inst.invert_SNAIL = self.invert_SNAIL

		SNAIL_inst.jj_bottom_layer = self.jj_bottom_layer
		SNAIL_inst.jj_top_layer = self.jj_top_layer
		SNAIL_inst.small_jj_top_layer = self.small_jj_top_layer
		self.SNAIL_1 = SNAIL_inst.generateCell()

		self.JJ_large = SNAIL_inst.JJ_large
		self.JJ_small = SNAIL_inst.JJ_small

		self.x_size_of_large_JJ = SNAIL_inst.x_size_of_large_JJ
		self.y_size_of_large_JJ = SNAIL_inst.y_size_of_large_JJ
		self.x_size_of_small_JJ = SNAIL_inst.x_size_of_small_JJ
		self.y_size_of_small_JJ = SNAIL_inst.y_size_of_small_JJ

		# adding a second SNAIL

		x_pos = 0
		y_pos = 0

		x_length_SNAIL_1 = SNAIL_inst.x_size_of_cell
		y_height_SNAIL_1 = SNAIL_inst.y_size_of_cell

		cell_out = gdstk.Cell("SNAILcell")

		SNAIL_1 = gdstk.Reference(self.SNAIL_1, origin=(x_pos,y_pos), rotation=0)

		cell_out.add(SNAIL_1)

		SNAIL_inst.height_jj_large = self.height_jj_large_arr[1]
		SNAIL_inst.height_jj_small = self.height_jj_small_arr[1]
		SNAIL_inst.ground_capacitance_pads_height = self.ground_capacitance_pads_height_arr[1]

		self.SNAIL_2 = SNAIL_inst.generateCell()

		self.JJ_large = SNAIL_inst.JJ_large
		self.JJ_small = SNAIL_inst.JJ_small

		self.x_size_of_large_JJ = SNAIL_inst.x_size_of_large_JJ
		self.y_size_of_large_JJ = SNAIL_inst.y_size_of_large_JJ
		self.x_size_of_small_JJ = SNAIL_inst.x_size_of_small_JJ
		self.y_size_of_small_JJ = SNAIL_inst.y_size_of_small_JJ
		x_length_SNAIL_2 = SNAIL_inst.x_size_of_cell
		y_height_SNAIL_2 = SNAIL_inst.y_size_of_cell

		if self.invert_SNAIL:

			SNAIL_2 = gdstk.Reference(self.SNAIL_2, origin=(x_pos + x_length_SNAIL_1 + x_length_SNAIL_2,y_pos), rotation=np.pi)
			# SNAIL_2 = gdstk.Reference(self.SNAIL, origin=(x_pos + 2*x_length_SNAIL-SNAIL_inst.litho_overlap,y_pos + SNAIL_inst.height_jj_large - SNAIL_inst.height_jj_small), x_reflection = True, rotation = np.pi)
		else:

			SNAIL_2 = gdstk.Reference(self.SNAIL_2, origin=(x_pos + x_length_SNAIL_1 + x_length_SNAIL_2,y_pos), x_reflection = True, rotation = np.pi)

		cell_out.add(SNAIL_2)
		
		cell_out.flatten()

		# self.x_size_of_cell = x_length_SNAIL_1 + x_length_SNAIL_2 - SNAIL_inst.litho_overlap
		self.x_size_of_cell = x_length_SNAIL_1 + x_length_SNAIL_2

		if self.invert_SNAIL:

			# self.y_size_of_cell = y_height_SNAIL_1 + SNAIL_inst.ground_capacitance_pads_height
			self.y_size_of_cell = y_height_SNAIL_1

		else:

			self.y_size_of_cell = y_height_SNAIL_1

		return cell_out


class LHcell:
	'''
	Class to generate the unit cell for a Left-Handed Josephson Transmission Line
	  There is one function:
		2) generateCell: generate the unit cell of LHJTL with one capacitor connected to a chain of junction using the classes Overlap_jj and Overlap_capa
		The variable self.x_size_of_cell and self.y_size_of_cell store sizes of the structure for global use
		Note that it stores the variables self.x_size_of_cell and self.y_size_of_cell of the classes Overlap_jj and Overlap_capa in the
		variables:
		1) x_size_of_capa
		2) y_size_of_capa
		3) x_size_of_jj
		4) y_size_of_jj
	'''

	def __init__(self):

		# self.spacing_jj = 2.0
		# self.spacing_capa = 2.0
		# self.electrode_height_difference = 5.0
		# self.number_of_capacitors = 2
		# self.y_low_current_ground = 3.0

		self.litho_overlap = None
		self.etching_offset = None
		
		self.width_jj = None
		self.height_jj = None
		self.spacing_jj = None
		self.number_of_junctions = None

		self.height_capa = None
		self.width_capa = None
		self.spacing_capa = None
		self.electrode_height_difference_JJ = None
		self.electrode_height_difference_capa = None
		self.number_of_capacitors = None

		self.y_low_current_ground = None

		self.jj_bottom_layer = 1
		self.capa_bottom_layer = 2
		self.jj_top_layer = 3
		self.capa_top_layer = 4
		self.ground_layer = 5

		self.cells_in_element = 1


	def generateCell(self, **kwargs):

		if 'change_area_capa' in kwargs:
			change_area_capa = kwargs.get("change_area_capa")
		else:
			change_area_capa = False

		PPC_inst = Overlap_capa()
		PPC_inst.litho_overlap = self.litho_overlap
		PPC_inst.etching_offset = self.etching_offset
		PPC_inst.height_capa = self.height_capa
		PPC_inst.width_capa = self.width_capa
		PPC_inst.spacing_capa = self.spacing_capa
		PPC_inst.electrode_height_difference = self.electrode_height_difference_capa
		PPC_inst.capa_bottom_layer = self.capa_bottom_layer
		PPC_inst.capa_top_layer = self.capa_top_layer
		PPC_inst.y_low_current_ground = self.y_low_current_ground
		self.PPC = PPC_inst.generateCell(change_area_capa=change_area_capa)

		JJ_inst = Overlap_jj()
		JJ_inst.litho_overlap = self.litho_overlap
		JJ_inst.etching_offset = self.etching_offset
		JJ_inst.y_low_current_ground = self.y_low_current_ground
		JJ_inst.height_jj = self.height_jj
		JJ_inst.spacing_jj = self.spacing_jj
		JJ_inst.jj_top_layer = self.jj_top_layer
		JJ_inst.width_jj = self.width_jj + self.etching_offset
		JJ_inst.electrode_height_difference = self.electrode_height_difference_JJ
		JJ_inst.jj_bottom_layer = 101
		JJ_to_ground = JJ_inst.generateCell()
		JJ_inst.width_jj = self.width_jj
		JJ_inst.jj_bottom_layer = self.jj_bottom_layer
		self.JJ = JJ_inst.generateCell()

		litho_overlap = self.litho_overlap 

		number_of_junctions = self.number_of_junctions
		number_of_capacitors = self.number_of_capacitors
		etching_offset = self.etching_offset
		
		ground_layer = self.ground_layer

		# generate cell to add features to
		cell_out = gdstk.Cell("LHcell")

		# add PPC
		x_pos = 0
		y_pos = 0
		x_increment = PPC_inst.x_size_of_cell

		for i in range(number_of_capacitors):
			if i%2 == 0:
				PPC_ref = gdstk.Reference(self.PPC, origin=(x_pos+i*x_increment,y_pos))
			else:
				PPC_ref = gdstk.Reference(self.PPC, origin=(x_pos+(i+1)*x_increment,y_pos), rotation=np.pi)
			cell_out.add(PPC_ref)

		# add chain of junctions
		x_pos += 2*PPC_inst.x_size_of_cell
		y_pos -= PPC_inst.y_size_of_cell
		y_increment = JJ_inst.x_size_of_cell

		for i in range(number_of_junctions):
			if i%2 == 0:
				JJ_ref = gdstk.Reference(self.JJ, origin=(x_pos,y_pos-i*y_increment), rotation=-np.pi/2)
			elif i == number_of_junctions-1:
				JJ_ref = gdstk.Reference(JJ_to_ground, origin=(x_pos,y_pos-(i+1)*y_increment-etching_offset), x_reflection=True, rotation=np.pi/2)
			else:
				JJ_ref = gdstk.Reference(self.JJ, origin=(x_pos,y_pos-(i+1)*y_increment), x_reflection=True, rotation=np.pi/2)
			cell_out.add(JJ_ref)

		y_pos -= number_of_junctions*y_increment + litho_overlap/2.0

		# add ground
		points_ground = [(0, 0), 
						(0, -PPC_inst.y_size_of_cell-PPC_inst.y_low_current_ground), 
						(2.0*PPC_inst.x_size_of_cell-JJ_inst.y_size_of_cell-JJ_inst.y_low_current_ground, -PPC_inst.y_size_of_cell-PPC_inst.y_low_current_ground), 
						(2.0*PPC_inst.x_size_of_cell-JJ_inst.y_size_of_cell-JJ_inst.y_low_current_ground, y_pos), 
						(2.0*PPC_inst.x_size_of_cell+JJ_inst.y_size_of_cell+JJ_inst.y_low_current_ground, y_pos), 
						(2.0*PPC_inst.x_size_of_cell+JJ_inst.y_size_of_cell+JJ_inst.y_low_current_ground, -PPC_inst.y_size_of_cell), 
						(2.0*PPC_inst.x_size_of_cell, -PPC_inst.y_size_of_cell), 
						(2.0*PPC_inst.x_size_of_cell, PPC_inst.y_size_of_cell+PPC_inst.y_low_current_ground), 
						(JJ_inst.y_size_of_cell, PPC_inst.y_size_of_cell+PPC_inst.y_low_current_ground), 
						(JJ_inst.y_size_of_cell, PPC_inst.y_size_of_cell), 
						(0, PPC_inst.y_size_of_cell)]

		ground = gdstk.Polygon(points_ground, layer=ground_layer)

		cell_out.flatten()

		self.x_size_of_capa = PPC_inst.x_size_of_cell
		self.y_size_of_capa = PPC_inst.y_size_of_cell
		self.x_size_of_jj = JJ_inst.x_size_of_cell
		self.y_size_of_jj = JJ_inst.y_size_of_cell
		self.x_size_of_cell = number_of_capacitors*PPC_inst.x_size_of_cell
		self.x_size_of_cell_tot = self.x_size_of_cell + PPC_inst.width_capa + PPC_inst.spacing_capa/2
		# self.x_size_of_cell_tot = self.x_size_of_cell + (JJ_inst.height_jj/2 + JJ_inst.electrode_height_difference)
		self.y_size_of_cell = y_pos

		return cell_out


#This part does not run when imported as module
if __name__ == '__main__':

	test_TaperedPad = True
	test_Pad = True
	test_Pad_CPW = True
	test_Pad_CPW_ground = True
	test_Pad_inv_microstrip = True
	test_Pad_bonding = True
	test_feedline = True
	test_feedline_CPW = True
	test_meander = True
	test_LER = True
	test_LER_no_ground = True
	test_overlap_jj = True
	test_overlap_capa = True
	test_RHTWPA = True
	test_OverlapSNAIL = True
	test_SNAILTWPA = True
	test_LHTWPA = True
	test_overlap_res = True


	if test_overlap_jj:
		lib = gdstk.Library()
		cell_out = gdstk.Cell("out")

		Overlap_inst = Overlap_jj()

		Overlap_inst.height_jj = 2.5
		Overlap_inst.width_jj = 10.0/2.5
		Overlap_inst.spacing_jj = 2.0
		Overlap_inst.litho_overlap = 0.1
		Overlap_inst.electrode_height_difference = 0.5
		Overlap_inst.y_low_current_ground = 3.0



		Overlap = Overlap_inst.generateCell(add_ground=False)

		for i in range(1):
			if i%2 == 0:
				ref = gdstk.Reference(Overlap, origin=(i*Overlap_inst.x_size_of_cell,0), rotation=0)
			else:
				ref = gdstk.Reference(Overlap, origin=((i+1)*Overlap_inst.x_size_of_cell,0), rotation=np.pi)
			cell_out.add(ref)

		cell_out.flatten()

		# Save the layout
		lib.add(cell_out)
		lib.write_gds('test_elements/Overlap_jj.gds')


	if test_overlap_capa:
		lib = gdstk.Library()
		cell_out = gdstk.Cell("out")

		Overlap_inst = Overlap_capa()

		Overlap_inst.height_capa = 20.0
		Overlap_inst.width_capa = 5.0
		Overlap_inst.spacing_capa = 2.0
		Overlap_inst.new_area_capa = Overlap_inst.width_capa*Overlap_inst.height_capa
		Overlap_inst.litho_overlap = 0.01
		Overlap_inst.electrode_height_difference = 1.5
		Overlap_inst.y_low_current_ground = 3.0

		Overlap = Overlap_inst.generateCell(add_ground=True)

		for i in range(1):
			if i%2 == 0:
				ref = gdstk.Reference(Overlap, origin=(i*Overlap_inst.x_size_of_cell,0), rotation=0)
			else:
				ref = gdstk.Reference(Overlap, origin=((i+1)*Overlap_inst.x_size_of_cell,0), rotation=np.pi)
			cell_out.add(ref)

		cell_out.flatten()

		# Save the layout
		lib.add(cell_out)
		lib.write_gds('test_elements/Overlap_capa.gds')


	if test_Pad:
		lib = gdstk.Library()

		cell_out = gdstk.Cell('cell_out')
		
		Pad_inst = Pad()
		Pad_inst.CPW = False
		Pad_inst.Exclude_ground = False
		pad = Pad_inst.GeneratePad()
		pad_ref = gdstk.Reference(pad, origin=(0,0), rotation=0)
		cell_out.add(pad_ref)

		cell_out.flatten()

		lib.add(cell_out)
		lib.write_gds('test_elements/Pad.gds')


	if test_Pad_CPW:
		lib = gdstk.Library()

		cell_out = gdstk.Cell('cell_out')
		
		Pad_inst = Pad()
		Pad_inst.CPW = True
		Pad_inst.Exclude_ground = True
		
		Pad_inst.x_pad = 150
		Pad_inst.y_pad = 300
		Pad_inst.x_arm = 20
		Pad_inst.y_arm = 40
		Pad_inst.taper_length = 50
		Pad_inst.x_pad_gap = 50
		Pad_inst.y_pad_gap = 175
		Pad_inst.arm_gap = 21

		pad = Pad_inst.GeneratePad()
		pad_ref = gdstk.Reference(pad, origin=(0,0), rotation=0)
		cell_out.add(pad_ref)

		cell_out.flatten()

		lib.add(cell_out)
		lib.write_gds('test_elements/Pad_CPW.gds')

	if test_Pad_CPW_ground:
		lib = gdstk.Library()

		cell_out = gdstk.Cell('cell_out')
		
		Pad_inst = Pad()
		Pad_inst.CPW = True
		Pad_inst.Exclude_ground = False
		
		Pad_inst.x_pad = 150
		Pad_inst.y_pad = 300
		Pad_inst.x_arm = 20
		Pad_inst.y_arm = 40
		Pad_inst.taper_length = 50
		Pad_inst.x_pad_gap = 50
		Pad_inst.y_pad_gap = 175
		Pad_inst.arm_gap = 21

		Pad_inv = Pad_inst.GeneratePad()
		pad_ref = gdstk.Reference(Pad_inv, origin=(0,0), rotation=0)
		cell_out.add(pad_ref)

		cell_out.flatten()

		lib.add(cell_out)
		lib.write_gds('test_elements/Pad_CPW_ground.gds')

	if test_Pad_bonding:

		lib = gdstk.Library()

		cell_out = gdstk.Cell('cell_out')

		Pad_inst = Pad_simple()

		pad = Pad_inst.Generate_Pad()
		pad_ref = gdstk.Reference(pad, origin=(0,0), rotation=0)
		cell_out.add(pad_ref)

		cell_out.flatten()

		lib.add(cell_out)
		lib.write_gds('test_elements/Pad_bonding.gds')

	if test_Pad_inv_microstrip:

		lib = gdstk.Library()
		cell_out = gdstk.Cell('cell_out')

		Pad_inst = Pad_TWPA_inv_microstrip()

		pad_inv = Pad_inst.Generate_Pad_TWPA()
		pad_ref = gdstk.Reference(pad_inv, origin=(0,0), rotation=0)
		cell_out.add(pad_ref)

		cell_out.flatten()

		lib.add(cell_out)
		lib.write_gds('test_elements/Pad_inv_microstrip.gds')


	if test_feedline:
		lib = gdstk.Library()

		Feedline_inst = FeedLine()
		Feedline_inst.CPW = False
		Feedline = Feedline_inst.GenerateFeedline()		

		lib.add(Feedline)
		lib.write_gds('test_elements/Feedline.gds')


	if test_feedline_CPW:
		lib = gdstk.Library()

		Feedline_inst = FeedLine()
		Feedline_inst.CPW = True
		Feedline_inst.x_pad = 150
		Feedline_inst.y_pad = 300
		Feedline_inst.x_arm = 20
		Feedline_inst.y_arm = 40
		Feedline_inst.taper_length = 25
		Feedline_inst.x_pad_gap = 10
		Feedline_inst.y_pad_gap = 135
		Feedline_inst.arm_gap = 21

		Feedline_inst.feedline_length = 4000
		Feedline_inst.feedline_width = 40
		Feedline_inst.feedline_gap = 21

		### Layer definition
		Feedline_inst.feedline_layer = 1
		Feedline_inst.ground_layer = 2
		feedline = Feedline_inst.GenerateFeedline()		

		lib.add(feedline)
		lib.write_gds('test_elements/Feedline_CPW.gds')


	if test_meander:
		lib = gdstk.Library()

		cell_out = gdstk.Cell('cell_out')
		
		Meander_inst = Meander()
		meander = Meander_inst.GenerateMeander()
		meander_ref = gdstk.Reference(meander, origin=(0,0), rotation=0)
		cell_out.add(meander_ref)

		cell_out.flatten()

		lib.add(cell_out)
		lib.write_gds('test_elements/Meander.gds')


	if test_LER:
		lib = gdstk.Library()

		cell_out = gdstk.Cell('cell_out')
		
		LER_inst = Overlap_LER()

		LER_inst.area_capa = 100
		# LER_inst.width_capa = 10
		LER_inst.spacing_between_capa = 6
		LER_inst.number_of_capacitors = 2

		LER = LER_inst.generateCell(reflection=False)
		LER_ref = gdstk.Reference(LER, origin=(0,0), rotation=0)
		cell_out.add(LER_ref)

		cell_out.flatten()

		lib.add(cell_out)
		lib.write_gds('test_elements/LER.gds')


	if test_LER_no_ground:
		lib = gdstk.Library()

		cell_out = gdstk.Cell('cell_out')
		
		LER_inst = Overlap_LER()

		LER_inst.CPW = False
		LER_inst.area_capa = 100
		# LER_inst.width_capa = 10
		LER_inst.spacing_between_capa = 6
		LER_inst.number_of_capacitors = 2

		LER = LER_inst.generateCell()
		LER_ref = gdstk.Reference(LER, origin=(0,0), rotation=0)
		cell_out.add(LER_ref)

		cell_out.flatten()

		lib.add(cell_out)
		lib.write_gds('test_elements/LER_no_ground.gds')


	if test_RHTWPA:
		lib = gdstk.Library()

		cell_out = gdstk.Cell("RHcell")

		RHJTL_inst = RHcell()

		RHJTL_inst.litho_overlap = 0.1
		RHJTL_inst.etching_offset = 0.25
		RHJTL_inst.width_jj = 3.0
		RHJTL_inst.height_jj = 3.0
		RHJTL_inst.spacing_jj = 2.0
		RHJTL_inst.electrode_height_difference_jj = 0.5
		RHJTL_inst.number_of_junctions = 2
		RHJTL_inst.area_capa = 40.0
		RHJTL_inst.new_area_capa = RHJTL_inst.area_capa
		RHJTL_inst.spacing_capa = 2.0
		RHJTL_inst.electrode_height_difference_capa = 1.5
		RHJTL_inst.number_of_capacitors = 2
		RHJTL_inst.y_low_current_ground = 3.0

		RHJTL = RHJTL_inst.generateCell()

		for i in range(1):
			if i%2 == 0:
				RHJTL_ref = gdstk.Reference(RHJTL, origin=(i*RHJTL_inst.x_size_of_cell,0))
			else:
				RHJTL_ref = gdstk.Reference(RHJTL, origin=(i*RHJTL_inst.x_size_of_cell,0), rotation=0)
			cell_out.add(RHJTL_ref)

		cell_out.flatten()
		lib.add(cell_out)
		lib.write_gds('test_elements/RH.gds')

	if test_OverlapSNAIL:
		lib = gdstk.Library()

		cell_out = gdstk.Cell("SNAILcell")

		SNAIL_inst = Overlap_SNAIL()

	
		SNAIL_inst.litho_overlap = 0.1
		SNAIL_inst.etching_offset = 0.25

		SNAIL_inst.area_ratio = 0.1
		SNAIL_inst.width_jj_large = 0.7
		SNAIL_inst.height_jj_large = 4
		SNAIL_inst.spacing_jj_large = 1
		SNAIL_inst.electrode_height_difference_jj = 0.5
		SNAIL_inst.number_of_large_junctions = 3

		
		SNAIL_inst.width_jj_small = 1
		SNAIL_inst.height_jj_small = SNAIL_inst.area_ratio*SNAIL_inst.height_jj_large
		
		SNAIL_inst.loop_area = 24.1
		SNAIL_inst.loop_arm_width = SNAIL_inst.spacing_jj_large/2
		SNAIL_inst.loop_width = SNAIL_inst.number_of_large_junctions * (SNAIL_inst.width_jj_large + SNAIL_inst.spacing_jj_large) # Defined as is because the size of loop arms is calculated upon the size of a JJ element (1*JJ_width + 2*JJ_spacing)
		SNAIL_inst.loop_height = SNAIL_inst.loop_area / (SNAIL_inst.loop_width - SNAIL_inst.loop_arm_width)
		

		SNAIL_inst.ground_capacitance_pads_height = 10
		SNAIL_inst.ground_capacitance_pads_width = 0.75

		
		SNAIL = SNAIL_inst.generateCell()

		for i in range(1):
			if i%2 == 0:
				SNAIL_ref = gdstk.Reference(SNAIL, origin=(i*SNAIL_inst.x_size_of_cell,0))
			else:
				SNAIL_ref = gdstk.Reference(SNAIL, origin=(i*SNAIL_inst.x_size_of_cell,0), rotation=0)
			cell_out.add(SNAIL_ref)

		cell_out.flatten()
		lib.add(cell_out)
		lib.write_gds('test_elements/SNAIL.gds')

	if test_SNAILTWPA:
		lib = gdstk.Library()

		cell_out = gdstk.Cell("SNAILcell")

		SNAILTL_inst = SNAILcell()

		SNAILTL_inst.modulation = 'False' # If you want to test 'True', which is simply automatically set when asking for a modulated SNAIL chain, an 2-element array has to be passed to  height_jj_large, height_jj_small and ground_capacitance_pads_height
		SNAILTL_inst.modulate_capa_only = 'False'
		SNAILTL_inst.keep_Z_constant_with_modulation = 'False'
		SNAILTL_inst.litho_overlap = 0.1
		SNAILTL_inst.etching_offset = 0.25
		SNAILTL_inst.area_ratio = 0.1
		SNAILTL_inst.width_jj_large = 1
		SNAILTL_inst.height_jj_large = 4
		SNAILTL_inst.spacing_jj_large = 1
		SNAILTL_inst.electrode_height_difference_jj = 0.5
		SNAILTL_inst.number_of_large_junctions = 3
	
		SNAILTL_inst.width_jj_small = 1
		SNAILTL_inst.height_jj_small = SNAILTL_inst.area_ratio*SNAILTL_inst.height_jj_large

		
		SNAILTL_inst.loop_area = 24
		SNAILTL_inst.loop_arm_width = SNAILTL_inst.spacing_jj_large/2
		SNAILTL_inst.loop_width = SNAILTL_inst.number_of_large_junctions * (SNAILTL_inst.width_jj_large + SNAILTL_inst.spacing_jj_large) # Defined as is because the size of bottom loop arms is calculated upon the size of a JJ element (1*JJ_width + 2*JJ_spacing)
		SNAILTL_inst.loop_height = SNAILTL_inst.loop_area / (SNAILTL_inst.loop_width - SNAILTL_inst.loop_arm_width)
		

		SNAILTL_inst.ground_capacitance_pads_height = 10
		SNAILTL_inst.ground_capacitance_pads_width = 0.75

		SNAILTL_inst.invert_SNAIL = True

		

		SNAILTL = SNAILTL_inst.generateCell()

		for i in range(1):
			if i%2 == 0:
				SNAILTL_ref = gdstk.Reference(SNAILTL, origin=(i*SNAILTL_inst.x_size_of_cell,0))
			else:
				SNAILTL_ref = gdstk.Reference(SNAILTL, origin=(i*SNAILTL_inst.x_size_of_cell,0), rotation=0)
			cell_out.add(SNAILTL_ref)

		cell_out.flatten()
		lib.add(cell_out)
		lib.write_gds('test_elements/SNAIL_cell.gds')


	if test_LHTWPA:
		lib = gdstk.Library()

		cell_out = gdstk.Cell("LHcell")

		LHJTL_inst = LHcell()

		LHJTL_inst.litho_overlap = 0.1
		LHJTL_inst.etching_offset = 0.25
		LHJTL_inst.width_jj = 2.0
		LHJTL_inst.height_jj = 5.0
		LHJTL_inst.spacing_jj = 2.0
		LHJTL_inst.number_of_junctions = 12
		LHJTL_inst.electrode_height_difference_JJ = 0.5

		area_capa = 100.0
		LHJTL_inst.width_capa = 5.0
		LHJTL_inst.height_capa = area_capa/LHJTL_inst.width_capa

		LHJTL_inst.spacing_capa = 2.0
		LHJTL_inst.number_of_capacitors = 2
		LHJTL_inst.y_low_current_ground = 3.0
		LHJTL_inst.electrode_height_difference_capa = 5.0

		LHJTL = LHJTL_inst.generateCell()

		for i in range(1):
			if i%2 == 0:
				LHJTL_ref = gdstk.Reference(LHJTL, origin=(i*LHJTL_inst.x_size_of_cell,0))
			else:
				LHJTL_ref = gdstk.Reference(LHJTL, origin=(i*LHJTL_inst.x_size_of_cell,0), x_reflection=True)
			cell_out.add(LHJTL_ref)

		cell_out.flatten()
		lib.add(cell_out)
		lib.write_gds('test_elements/LH.gds')


	if test_overlap_res:
		lib = gdstk.Library()

		cell_out = gdstk.Cell("Overlap_Res")

		Res_inst = Overlap_LER()

		Res_inst.width_jj = 3.0
		Res_inst.height_jj = 3.0
		Res_inst.spacing_jj = 2.0

		Res_inst.area_capa = 40.0
		
		Res = Res_inst.generateCell()

		# cell_out.add(Res)

		Res.flatten()
		lib.add(Res)
		lib.write_gds('test_elements/Overlap_res.gds')