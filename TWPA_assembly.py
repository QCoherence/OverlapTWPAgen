"""

This module can be used to generate the GDS of a TWPA or of a lumped element resonator coupled to a feedline
It chains unit cells and can create different test structures.

Implemented devices:
1) SJ: chain of junctions with top ground
2) RK: chain of SNAILs with top ground
3) RH: chain of junctions with capacitors to ground (modulation with only even number of cells per period)
4) LH: chain of capacitors with junctions arrays to ground
5) LER: a feedline with lumped element resonators coupled to it

"""

import gdstk
import numpy as np
import datetime
from TWPA_elements import Pad, Pad_TWPA_inv_microstrip

class TWPA_assembly():

    def __init__(self):

        self.device = None

        ### chip and writing parameters
        self.grid_size = (8,8)
        self.write_field = 0.25
        self.markers_layer = 101
        self.mean_field_layer = 102
        self.alignment_marker_size_um = 8

        ### resonators parameters
        self.feedline = None
        self.feedline_width = None
        self.resonators_chip_edge_spacing = 1000
        self.resonators_coupling_gap = None
        self.dicing_gap = 50

        ### bonding pads parameters
        self.x_pad = 150
        self.y_pad = 300 
        self.taper_length = 25
        self.x_pad_gap = 50
        self.y_pad_gap = 175 
        self.y_arm = 40
        self.arm_gap = 21

        ### Inverted microstrip bonding pad and connecting line parameters
        # These parameters are default parameters optimized by SW for 50 nm of Al2O3 deposited with ALD for the top ground
        
        self.y_pad_inv  = 100 # Do not change
        self.x_pad_inv = 280 # Do not change
        self.x_pad_inv_gap    = 10 # Do not change
        self.y_pad_inv_gap    = 15 # Do not change
        
        self.x_connecting_line = None
        self.y_connecting_line  = 4 # Do not change
        self.connecting_line_gap    = 13 # Do not change
        self.pad_line_overlap       = 2 # You can change but not a relevant parmater
        
        self.capacitance_along_connecting_line_width       = 2 # Do not change
        self.capacitance_along_connecting_line_pitch_first = 90 # Do not change
        self.capacitance_along_connecting_line_pitch       = 100 # Do not change

        ### chain unit cell parameters
        self.unit_cell = None
        self.unit_cell_size = None
        self.cells_in_element = 1
        self.unit_cell_height = None
        self.spacing_jj = None
        self.spacing_capa = None
        self.n_unit_cells = -1
        self.element_arr = []
        self.modulation_period = None
        self.modulation = False

        ### test chain parameters
        self.unit_cell_jj = None
        self.x_size_jj = None
        self.y_size_jj = None
        self.cells_in_element_jj = 1
        self.unit_cell_capa = None
        self.x_size_capa = None
        self.y_size_capa = None
        self.cells_in_element_capa = 1
        self.probe_pad_size = 100
        self.length_of_connecting_wire = 20
        self.width_of_connecting_wire = 5

        ### wet etching test dimensions
        self.trench_width = [1,2,5,10]
        self.trench_length = 180
        self.trench_gap = 10

        ### overlap between structures for litho
        self.Pad_litho_overlap = 1
        self.litho_overlap = 0.1

        ### Layer definition
        self.pad_bottom_layer = None
        self.connection_wire_bottom_layer = None
        self.jj_bottom_layer = None
        self.capa_bottom_layer = None
        self.ground_layer = None
        self.pad_top_layer = None
        self.connection_wire_top_layer = None

        ### tests and labels positions
        self.x_TC_capa = 3*self.write_field*1000
        self.y_TC_capa = self.grid_size[1]*1000 - 3*self.write_field*1000
        self.x_TC_jj = 3*self.write_field*1000
        self.y_TC_jj = 5*self.write_field*1000
        self.label_shift = 50
        self.x_chip_label = self.x_TC_jj - 2*self.label_shift
        self.y_cumulative  = self.y_TC_jj
        self.x_logo_CNRS = self.grid_size[0]*1000 - 3000
        self.x_logo_Neel = self.grid_size[0]*1000 - 2000
        self.y_logo = self.grid_size[1]*1000 - 1500
        self.x_wafer_label = 491.5 
        self.y_wafer_label = 7321
        self.x_R4t = self.grid_size[0]*1000 - 6*self.write_field*1000
        self.y_R4t = 3.25*self.write_field*1000
        self.x_WET = 3*self.write_field*1000
        self.y_WET = self.grid_size[1]*1000 - 3.25*self.write_field*1000

        ### tests and labels generation
        self.generate_test_chains_jj = True
        self.generate_test_chains_capa = True
        self.generate_test_chains_SNAIL = False
        self.add_R4t_Al = True
        self.add_wet_etching_test = True
        self.add_label = True
        self.add_wafer_label = True
        self.wafer_label = 'WafID'
        self.dev_label = 'Left DevID'
        self.text_size = 200
        self.add_logo_CNRS = True
        self.add_logo_Neel = True
        self.sizeOfPixel = 4

        self.save_location = 'test.gds'

    def get_layers_from_cell(self, cell):

        list_of_layers = []
        polygons = cell.get_polygons(True)
        for p in polygons:
            if p.layer not in list_of_layers:
                list_of_layers.append(p.layer)
        list_of_layers.sort()

        return list_of_layers


    def merge_object_per_layer(self, cell, layers_to_merge):

        cell_merged = gdstk.Cell("cell_merged")

        list_of_layers = self.get_layers_from_cell(cell)
        if layers_to_merge == 'all':
            layers_to_merge = list_of_layers
        for i in list_of_layers:
            cell_tmp = gdstk.Cell("cell_tmp")
            list_polygons = cell.get_polygons(layer=i,datatype=0)
            for j in range(0,len(list_polygons)):
                cell_tmp.add(list_polygons[j])
            ref = gdstk.Reference(cell_tmp,origin=(0,0),rotation=0)
            if i in layers_to_merge:
                ref_merged = gdstk.boolean(ref,[], "or", layer = i)
                for j in range(0,len(ref_merged)):
                    cell_merged.add(ref_merged[j])
            else:
                cell_merged.add(ref)

        return cell_merged


    def generate_chains(self,n_unit_cells,chain_type):
        '''
        This function generates chains of n unit cell, chain type can be:
        1) device for the device unit cell
        2) jj for the test chains of the jjs
        3) capa for the test chains of the capacitors
        '''
        cell = gdstk.Cell("chain")

        if chain_type == 'device':
            unit_cell = self.unit_cell
            unit_cell_size = self.unit_cell_size
        elif chain_type == 'jj':
            unit_cell = self.unit_cell_jj
            unit_cell_size= self.x_size_jj
        elif chain_type == 'capa':
            unit_cell = self.unit_cell_capa
            unit_cell_size= self.x_size_capa
        elif chain_type == 'jj_large':
            unit_cell = self.unit_cell_jj_large
            unit_cell_size= self.x_size_jj_large
        elif chain_type == 'jj_small':
            unit_cell = self.unit_cell_jj_small
            unit_cell_size= self.x_size_jj_small
        else:
            raise ValueError('Unrecognized chain type for chain generator.')



        for i in range(n_unit_cells):
            if chain_type == 'device':
                if self.modulation:
                    unit_cell = self.element_arr[i%int(self.modulation_period/self.cells_in_element)]
                if self.device == 'RH':
                    ref = gdstk.Reference(unit_cell, origin=(i*unit_cell_size,0))
                elif self.device == 'LH':
                    if i%2 == 0:
                        ref = gdstk.Reference(unit_cell, origin=(i*unit_cell_size,0))
                    else:
                        ref = gdstk.Reference(unit_cell, origin=(i*unit_cell_size,0), x_reflection=True)
                elif self.device == 'SJ':
                    if i%2 == 0:
                        ref = gdstk.Reference(unit_cell, origin=(i*unit_cell_size,0))
                    else:
                        ref = gdstk.Reference(unit_cell, origin=((i+1)*unit_cell_size,0), rotation=np.pi)
                elif self.device == 'SNAIL':
                    ref = gdstk.Reference(unit_cell, origin=(i*unit_cell_size,0))
                
                

            elif chain_type in ('jj', 'capa', 'jj_small', 'jj_large'):
                if i%2 == 0:
                    ref = gdstk.Reference(unit_cell, origin=(i*unit_cell_size,0))
                else:
                    ref = gdstk.Reference(unit_cell, origin=((i+1)*unit_cell_size,0), rotation=np.pi)

            
            cell.add(ref)

        return cell


    def generate_TC(self,n_unit_cells,chain_type):
        '''
        This function generates one test chain for junctions or capacitors
        '''
        cell = gdstk.Cell("test_chain")

        length_of_connecting_wire = self.length_of_connecting_wire
        probe_pad_size = self.probe_pad_size
        if chain_type == 'jj':
            unit_cell_size = self.x_size_jj
            width_of_connecting_wire = 2*self.y_size_jj
        elif chain_type == 'capa':
            unit_cell_size = self.x_size_capa
            width_of_connecting_wire = 2*self.y_size_capa
        elif chain_type == 'jj_small':
            unit_cell_size = self.x_size_jj_small
            width_of_connecting_wire = 2*self.y_size_jj_small
        elif chain_type == 'jj_large':
            unit_cell_size = self.x_size_jj_large
            width_of_connecting_wire = 2*self.y_size_jj_large
        Pad_litho_overlap = self.Pad_litho_overlap
        litho_overlap = self.litho_overlap
        pad_bottom_layer = self.pad_bottom_layer
        connection_wire_bottom_layer = self.connection_wire_bottom_layer
        pad_top_layer = self.pad_top_layer
        connection_wire_top_layer = self.connection_wire_top_layer

        ### Add probe pad
        x_pos_tic = 0
        probe_pad = gdstk.rectangle((0,-probe_pad_size/2), (probe_pad_size,probe_pad_size/2), layer=pad_bottom_layer)
        cell.add(probe_pad.copy().translate(x_pos_tic,0))
        x_pos_tic = probe_pad_size-Pad_litho_overlap

        ### Add common connecting wires
        common_wire = gdstk.rectangle((0,(0-width_of_connecting_wire)/2), (length_of_connecting_wire+Pad_litho_overlap,(0+width_of_connecting_wire)/2), layer=connection_wire_bottom_layer)
        cell.add(common_wire.copy().translate(x_pos_tic,0))
        x_pos_tic += length_of_connecting_wire+Pad_litho_overlap-litho_overlap/2

        ### Add elements
        test_chain = self.generate_chains(n_unit_cells,chain_type)
        ref_test_chain = gdstk.Reference(test_chain,origin=(x_pos_tic,0),rotation=0)
        cell.add(ref_test_chain)
        x_pos_tic += n_unit_cells*unit_cell_size-litho_overlap/2

        ### Add common connecting wires
        if n_unit_cells%2 == 0:
            common_wire = gdstk.rectangle((0,(0-width_of_connecting_wire)/2), (length_of_connecting_wire+Pad_litho_overlap,(0+width_of_connecting_wire)/2), layer=connection_wire_bottom_layer)
        else:
            common_wire = gdstk.rectangle((0,(0-width_of_connecting_wire)/2), (length_of_connecting_wire+Pad_litho_overlap,(0+width_of_connecting_wire)/2), layer=connection_wire_top_layer)
        cell.add(common_wire.copy().translate(x_pos_tic,0))
        x_pos_tic += length_of_connecting_wire

        ### Add probe pad
        if n_unit_cells%2 == 0:
            probe_pad = gdstk.rectangle((0,-probe_pad_size/2), (probe_pad_size,probe_pad_size/2), layer=pad_bottom_layer)
        else:
            probe_pad = gdstk.rectangle((0,-probe_pad_size/2), (probe_pad_size,probe_pad_size/2), layer=pad_top_layer)
        cell.add(probe_pad.copy().translate(x_pos_tic,0))
        x_pos_tic += probe_pad_size

        return cell


    def generate_TC_block(self, chain_type):
        '''
        This function generates the jj test chains block:
        1) The label top refers to the test chains in the top row
        2) The label bottom refers to the test chains in the bottom row
        ! For modulated TWPAs the jjs dimensions correspond to the mean value
        '''
        cell = gdstk.Cell("test_chain")
        cell_ret = gdstk.Cell("test_chain")

        if chain_type == 'jj':
            bottom_layer = self.jj_bottom_layer
        elif chain_type == 'capa':
            bottom_layer = self.capa_bottom_layer
        elif chain_type in ('jj_small', 'jj_large'):
            bottom_layer = self.jj_bottom_layer
        
        ground_layer = self.ground_layer
        pad_bottom_layer = self.pad_bottom_layer
        connection_wire_bottom_layer = self.connection_wire_bottom_layer
        pad_top_layer = self.pad_top_layer
        connection_wire_top_layer = self.connection_wire_top_layer
        probe_pad_size = self.probe_pad_size
        length_of_connecting_wire = self.length_of_connecting_wire   

        if chain_type == 'jj':
            unit_cell_size = self.x_size_jj
            elements = 10
            offset = 10
            n_chains_per_row = 5
        elif chain_type == 'capa':
            unit_cell_size = self.x_size_capa
            elements = 1
            offset = 1
            n_chains_per_row = 5
        elif chain_type == 'jj_small':
            unit_cell_size = self.x_size_jj_small
            elements = 10
            offset = 10
            n_chains_per_row = 5
        elif chain_type == 'jj_large':
            unit_cell_size = self.x_size_jj_large
            elements = 10
            offset = 10
            n_chains_per_row = 5

        x_pos = self.write_field*500 - (probe_pad_size + length_of_connecting_wire + 3*unit_cell_size)
        y_pos = 0

        for i in range(n_chains_per_row):
            n_elements = i*elements

            if self.device == 'SNAIL':
                n_bottom = 2*n_elements + offset

                if chain_type == 'jj_small':

                    TC_top = self.generate_TC(n_bottom,chain_type)
                    ref_TC_top = gdstk.Reference(TC_top,origin=(x_pos,probe_pad_size*0.75),rotation=0)
                    cell.add(ref_TC_top)
            
                elif chain_type == 'jj_large':
                    TC_bottom = self.generate_TC(n_bottom,chain_type)
                    ref_TC_bottom = gdstk.Reference(TC_bottom,origin=(x_pos,-probe_pad_size*0.75),rotation=0)
                    cell.add(ref_TC_bottom)

            else:
                n_top = 2*n_elements + offset
                n_bottom = 2*(n_elements + offset)
                TC_top = self.generate_TC(n_top,chain_type)
                TC_bottom = self.generate_TC(n_bottom,chain_type)
                ref_TC_top = gdstk.Reference(TC_top,origin=(x_pos,probe_pad_size*0.75),rotation=0)
                ref_TC_bottom = gdstk.Reference(TC_bottom,origin=(x_pos,-probe_pad_size*0.75),rotation=0)
                cell.add(ref_TC_top)
                cell.add(ref_TC_bottom)
            
            x_pos += n_bottom*unit_cell_size+2.5*probe_pad_size+2*length_of_connecting_wire


        # if chain_type in ('jj','capa','jj_large'):
        x_pos_ground = probe_pad_size/2
        y_ground_dim = 3*probe_pad_size
        x_ground_dim = x_pos + probe_pad_size/2
        ground_block = gdstk.rectangle((0,-y_ground_dim/2), (x_ground_dim,y_ground_dim/2), layer=ground_layer).translate(-x_pos_ground,0)
        bottom_electrodes =  cell.get_polygons(layer=bottom_layer,datatype=0)
        cell.add(ground_block)
        cell_ret_ref = gdstk.Reference(cell,origin=(0,-y_ground_dim),rotation=0)
        cell_ret.add(cell_ret_ref)
                        


        if chain_type in ('jj', 'jj_large'):
            self.y_cumulative  += -y_ground_dim/2

        return cell_ret


    def generate_R4t_Al(self, **kwargs):
        '''
        This function generates the 4-probe measurement structures block
        to measure the resistance of the two layers that are deposited
        '''
        if 'Exclude_ground' in kwargs:
            Exclude_ground = kwargs.get("Exclude_ground")
        else:
            Exclude_ground = False

        cell = gdstk.Cell("R4t_Al")
        cell_tmp = gdstk.Cell("R4t_Al_tmp")
        
        probe_pad_size = self.probe_pad_size
        wire_width = 1
        overlap_pad = self.Pad_litho_overlap
        connecting_wire_width = self.width_of_connecting_wire
        wire_squares = 100
        wire_length = wire_width*wire_squares+2*4
        gap_between_pads_x = 150
        gap_between_pads_y = 40
        overlap_wires = 1
        connecting_wire_small_width = 1
        pad_bottom_layer = self.pad_bottom_layer
        pad_top_layer = self.pad_top_layer
        connection_wire_bottom_layer = self.connection_wire_bottom_layer
        connection_wire_top_layer = self.connection_wire_top_layer
        ground_layer = self.ground_layer
        
        ### R4t of first layer
        x_pos_tic = 0
        y_pos_tic = 0

        probe_pad = gdstk.rectangle((0,0), (probe_pad_size,probe_pad_size), layer=pad_bottom_layer)
        cell.add(probe_pad.copy().translate(x_pos_tic,0))
        cell.add(probe_pad.copy().translate(x_pos_tic+probe_pad_size+gap_between_pads_x,0))
        cell.add(probe_pad.copy().translate(x_pos_tic,probe_pad_size+gap_between_pads_y))
        cell.add(probe_pad.copy().translate(x_pos_tic+probe_pad_size+gap_between_pads_x,probe_pad_size+gap_between_pads_y))

        x_wire_pos = x_pos_tic+probe_pad_size+gap_between_pads_x/2-wire_length/2
        y_wire_pos = y_pos_tic+probe_pad_size+gap_between_pads_y/2-wire_width/2

        Al_wire = gdstk.rectangle((0,0), (wire_length,wire_width), layer=connection_wire_bottom_layer)
        cell.add(Al_wire.copy().translate(x_wire_pos,y_wire_pos))

        connecting_wire_length_big = gap_between_pads_x/2-wire_length/2+overlap_pad+overlap_wires+1
        connecting_wire_I_big = gdstk.rectangle((0,0), (connecting_wire_length_big,connecting_wire_width), layer=connection_wire_bottom_layer)
        connecting_wire_V_big = gdstk.rectangle((0,0), (connecting_wire_length_big+2,connecting_wire_width), layer=connection_wire_bottom_layer)
        cell.add(connecting_wire_I_big.copy().translate(x_pos_tic+probe_pad_size-overlap_pad,probe_pad_size+gap_between_pads_y))
        cell.add(connecting_wire_I_big.copy().translate(x_pos_tic+probe_pad_size+overlap_pad+gap_between_pads_x-connecting_wire_length_big,probe_pad_size+gap_between_pads_y))
        cell.add(connecting_wire_V_big.copy().translate(x_pos_tic+probe_pad_size-overlap_pad,probe_pad_size-connecting_wire_width))
        cell.add(connecting_wire_V_big.copy().translate(x_pos_tic+probe_pad_size+overlap_pad+gap_between_pads_x-connecting_wire_length_big-2,probe_pad_size-connecting_wire_width))

        connecting_wire_length_small = gap_between_pads_y/2+1.5
        connecting_wire_small = gdstk.rectangle((0,0), (connecting_wire_small_width,connecting_wire_length_small+connecting_wire_width), layer=connection_wire_bottom_layer)
        cell.add(connecting_wire_small.copy().translate(x_pos_tic+probe_pad_size+connecting_wire_length_big+2-overlap_pad-1,probe_pad_size-connecting_wire_width))
        cell.add(connecting_wire_small.copy().translate(x_pos_tic+probe_pad_size+gap_between_pads_x-connecting_wire_length_big-2+overlap_pad,probe_pad_size-connecting_wire_width))
        cell.add(connecting_wire_small.copy().translate(x_pos_tic+probe_pad_size+connecting_wire_length_big-overlap_pad-1,probe_pad_size+gap_between_pads_y-connecting_wire_length_small))
        cell.add(connecting_wire_small.copy().translate(x_pos_tic+probe_pad_size+gap_between_pads_x-connecting_wire_length_big+overlap_pad,probe_pad_size+gap_between_pads_y-connecting_wire_length_small))

        ### R4t of second layer
        x_pos_tic = 2.5*probe_pad_size+gap_between_pads_x
        y_pos_tic = 0

        probe_pad = gdstk.rectangle((0,0), (probe_pad_size,probe_pad_size), layer=pad_top_layer)
        cell.add(probe_pad.copy().translate(x_pos_tic,0))
        cell.add(probe_pad.copy().translate(x_pos_tic+probe_pad_size+gap_between_pads_x,0))
        cell.add(probe_pad.copy().translate(x_pos_tic,probe_pad_size+gap_between_pads_y))
        cell.add(probe_pad.copy().translate(x_pos_tic+probe_pad_size+gap_between_pads_x,probe_pad_size+gap_between_pads_y))
        
        x_wire_pos = x_pos_tic+probe_pad_size+gap_between_pads_x/2-wire_length/2
        y_wire_pos = y_pos_tic+probe_pad_size+gap_between_pads_y/2-wire_width/2

        Al_wire = gdstk.rectangle((0,0), (wire_length,wire_width), layer=connection_wire_top_layer)
        cell.add(Al_wire.copy().translate(x_wire_pos,y_wire_pos))
                
        connecting_wire_length_big = gap_between_pads_x/2-wire_length/2+overlap_pad+overlap_wires+1
        connecting_wire_I_big = gdstk.rectangle((0,0), (connecting_wire_length_big,connecting_wire_width), layer=connection_wire_top_layer)
        connecting_wire_V_big = gdstk.rectangle((0,0), (connecting_wire_length_big+2,connecting_wire_width), layer=connection_wire_top_layer)
        cell.add(connecting_wire_I_big.copy().translate(x_pos_tic+probe_pad_size-overlap_pad,probe_pad_size+gap_between_pads_y))
        cell.add(connecting_wire_I_big.copy().translate(x_pos_tic+probe_pad_size+overlap_pad+gap_between_pads_x-connecting_wire_length_big,probe_pad_size+gap_between_pads_y))
        cell.add(connecting_wire_V_big.copy().translate(x_pos_tic+probe_pad_size-overlap_pad,probe_pad_size-connecting_wire_width))
        cell.add(connecting_wire_V_big.copy().translate(x_pos_tic+probe_pad_size+overlap_pad+gap_between_pads_x-connecting_wire_length_big-2,probe_pad_size-connecting_wire_width))
        
        connecting_wire_length_small = gap_between_pads_y/2+1.5
        connecting_wire_small = gdstk.rectangle((0,0), (connecting_wire_small_width,connecting_wire_length_small+connecting_wire_width), layer=connection_wire_top_layer)
        cell.add(connecting_wire_small.copy().translate(x_pos_tic+probe_pad_size+connecting_wire_length_big+2-overlap_pad-1,probe_pad_size-connecting_wire_width))
        cell.add(connecting_wire_small.copy().translate(x_pos_tic+probe_pad_size+gap_between_pads_x-connecting_wire_length_big-2+overlap_pad,probe_pad_size-connecting_wire_width))
        cell.add(connecting_wire_small.copy().translate(x_pos_tic+probe_pad_size+connecting_wire_length_big-overlap_pad-1,probe_pad_size+gap_between_pads_y-connecting_wire_length_small))
        cell.add(connecting_wire_small.copy().translate(x_pos_tic+probe_pad_size+gap_between_pads_x-connecting_wire_length_big+overlap_pad,probe_pad_size+gap_between_pads_y-connecting_wire_length_small))

        ### Add ground
        ground_block = gdstk.rectangle((0,0), (5*probe_pad_size+2*gap_between_pads_x,2.5*probe_pad_size+gap_between_pads_y), layer=ground_layer)
        ground_block.translate(-probe_pad_size/4, -probe_pad_size/4)

        if Exclude_ground:
            pads = cell.get_polygons(layer=pad_bottom_layer,datatype=0)
            wires = cell.get_polygons(layer=connection_wire_bottom_layer,datatype=0)
            ground_exclusion = gdstk.boolean(ground_block, pads + wires, 'not',  precision=1e-3, layer=ground_layer)

            cell.add(*ground_exclusion)
        else:
            cell.add(ground_block)

        return cell
 

    def generate_wet_etching_test(self):

        cell = gdstk.Cell("test_chain")
        cell_ret = gdstk.Cell("test_chain_WE")

        ground_layer = self.ground_layer    
        trench_width = self.trench_width
        trench_length = self.trench_length
        trench_gap = self.trench_gap
        y_pos_tic = 0

        for i in range(0,len(trench_width)):
            trench = gdstk.rectangle((0,-trench_width[i]/2), (trench_length,trench_width[i]/2), layer=ground_layer)
            if i==0:
                cell.add(trench.copy().translate(0,0))
            else:
                cell.add(trench.copy().translate(0,(y_pos_tic+trench_gap+trench_width[i-1]/2+trench_width[i]/2)))
                y_pos_tic = y_pos_tic + trench_gap + trench_width[i-1]/2 + trench_width[i]/2
            
        cell_ret_ref = gdstk.Reference(cell,origin=(0,0),rotation=0)
        cell_ret.add(cell_ret_ref)

        return cell_ret


    def generate_logo_CNRS(self):

        cell = gdstk.Cell("logo")

        pixel = gdstk.rectangle((0,0), (self.sizeOfPixel,self.sizeOfPixel), layer=self.ground_layer)
        logo_CNRS = np.load(self.installation_dir+'logo/logo_CNRS.npy')
        width = len(logo_CNRS)
        height = len(logo_CNRS[0])

        for x in range(width):
            for y in range(height):
                if logo_CNRS[x][y] == 0:
                    cell.add(pixel.copy().translate(self.sizeOfPixel*(x), self.sizeOfPixel*(height-y-1)))

        return cell


    def generate_logo_Neel(self):

        cell = gdstk.Cell("logo")

        pixel = gdstk.rectangle((0,0), (self.sizeOfPixel,self.sizeOfPixel), layer=self.ground_layer)
        logo_Neel = np.load(self.installation_dir+'logo/logo_Neel.npy')
        width = len(logo_Neel)
        height = len(logo_Neel[0])

        for x in range(width):
            for y in range(height):
                if logo_Neel[x][y] == 0:
                    cell.add(pixel.copy().translate(self.sizeOfPixel*(x), self.sizeOfPixel*(height-y-1)))

        return cell


    def generate_markers(self):

        cell = gdstk.Cell("Markers")

        ### Parameters definition
        grid_size = self.grid_size
        write_field = self.write_field
        alignment_marker_size_um = self.alignment_marker_size_um
        write_field_um = write_field*1000
        grid_size_um = (grid_size[0]*1000,grid_size[1]*1000)

        ### Layer definition
        markers_layer = self.markers_layer
        ground_layer = self.ground_layer
               
        ### Create markers, dicing markers and ground exclusion
        alignment_marker = gdstk.rectangle((-alignment_marker_size_um/2,-alignment_marker_size_um/2), (alignment_marker_size_um/2,alignment_marker_size_um/2), layer=markers_layer)
        ground_exclusion_sq = gdstk.Polygon([(0,0), (0,150), (150,150), (150,0)], layer=ground_layer)
        dicing_marker_LB = gdstk.Polygon([(0,0),(75,0),(100,25),(25,25),(25,100),(0,75)], layer=markers_layer)
        dicing_marker_TR = dicing_marker_LB.copy().rotate(np.pi)
        dicing_marker_RB = dicing_marker_LB.copy().rotate(np.pi/2)
        dicing_marker_LT = dicing_marker_RB.copy().rotate(np.pi)

        ### Add bottom left
        cell.add(alignment_marker.copy().translate(write_field_um,write_field_um))
        cell.add(alignment_marker.copy().translate(2*write_field_um,write_field_um))
        cell.add(alignment_marker.copy().translate(3*write_field_um,write_field_um))
        cell.add(alignment_marker.copy().translate(write_field_um,2*write_field_um))
        cell.add(alignment_marker.copy().translate(write_field_um,3*write_field_um))

        ### Add top left
        cell.add(alignment_marker.copy().translate(write_field_um,grid_size_um[1]-write_field_um))
        cell.add(alignment_marker.copy().translate(2*write_field_um,grid_size_um[1]-write_field_um))
        cell.add(alignment_marker.copy().translate(3*write_field_um,grid_size_um[1]-write_field_um))
        cell.add(alignment_marker.copy().translate(write_field_um,grid_size_um[1]-2*write_field_um))
        cell.add(alignment_marker.copy().translate(write_field_um,grid_size_um[1]-3*write_field_um))

        ### Add bottom right
        cell.add(alignment_marker.copy().translate(grid_size_um[0]-write_field_um,write_field_um))
        cell.add(alignment_marker.copy().translate(grid_size_um[0]-2*write_field_um,write_field_um))
        cell.add(alignment_marker.copy().translate(grid_size_um[0]-3*write_field_um,write_field_um))
        cell.add(alignment_marker.copy().translate(grid_size_um[0]-write_field_um,2*write_field_um))
        cell.add(alignment_marker.copy().translate(grid_size_um[0]-write_field_um,3*write_field_um))

        ### Add top right
        cell.add(alignment_marker.copy().translate(grid_size_um[0]-write_field_um,grid_size_um[1]-write_field_um))
        cell.add(alignment_marker.copy().translate(grid_size_um[0]-2*write_field_um,grid_size_um[1]-write_field_um))
        cell.add(alignment_marker.copy().translate(grid_size_um[0]-3*write_field_um,grid_size_um[1]-write_field_um))
        cell.add(alignment_marker.copy().translate(grid_size_um[0]-write_field_um,grid_size_um[1]-2*write_field_um))
        cell.add(alignment_marker.copy().translate(grid_size_um[0]-write_field_um,grid_size_um[1]-3*write_field_um))

        ### Add dicing markers
        cell.add(dicing_marker_LB.copy().translate(0,0))
        cell.add(dicing_marker_LT.copy().translate(0,0+grid_size_um[1]))
        cell.add(dicing_marker_RB.copy().translate(0+grid_size_um[0],0))
        cell.add(dicing_marker_TR.copy().translate(0+grid_size_um[0],0+grid_size_um[1]))

        ### Add ground exclusion
        cell.add(ground_exclusion_sq.copy().translate(0,0))
        cell.add(ground_exclusion_sq.copy().rotate(3*np.pi/2).translate(0,0+grid_size_um[1]))
        cell.add(ground_exclusion_sq.copy().rotate(np.pi/2).translate(0+grid_size_um[0],0))
        cell.add(ground_exclusion_sq.copy().rotate(np.pi).translate(0+grid_size_um[0],0+grid_size_um[1]))

        return cell


    def generate_TWPA_GDS(self):

        save_location = self.save_location

        lib = gdstk.Library()
        cell_save = gdstk.Cell("TWPA")
        cell = gdstk.Cell("TWPA_tmp")

        grid_size = self.grid_size
        write_field = self.write_field
        alignment_marker_size_um = self.alignment_marker_size_um
        write_field_um = write_field*1000
        grid_size_um = (grid_size[0]*1000,grid_size[1]*1000)

        x_pad = self.x_pad
        y_pad = self.y_pad
        taper_length = self.taper_length
        x_pad_gap = self.x_pad_gap
        y_pad_gap = self.y_pad_gap
        y_arm = self.y_arm
        arm_gap = self.arm_gap        

        unit_cell = self.unit_cell
        unit_cell_size = self.unit_cell_size
        unit_cell_height = self.unit_cell_height
        n_unit_cells = int(self.n_unit_cells/self.cells_in_element)
        x_size_jj = self.x_size_jj
        y_size_jj = self.y_size_jj
        x_size_capa = self.x_size_capa
        y_size_capa = self.y_size_capa
        spacing_jj = self.spacing_jj
        spacing_capa = self.spacing_capa

        if self.device in ('RH','LH'):

            x_size_of_cell_tot = self.unit_cell_size_tot

        litho_overlap = self.litho_overlap

        ground_layer = self.ground_layer
        pad_bottom_layer = self.pad_bottom_layer
        connection_wire_bottom_layer = self.connection_wire_bottom_layer
        if self.device in ('RH', 'SJ','SNAIL'):
            bottom_layer = self.jj_bottom_layer
        elif self.device == 'LH':
            bottom_layer = self.capa_bottom_layer

        ### Add markers
        markers = self.generate_markers()
        markers_ref = gdstk.Reference(markers, origin=(0,0))
        cell.add(markers_ref)

        ### Compute length of the chain
        chain_length = unit_cell_size*n_unit_cells

        ### Add bonding pads 
        if self.device == 'RH':
            y_taper_connection = 2*y_size_jj + 2*x_size_capa - spacing_capa # y size of the taper connecting the end of the arm to the beginning of the TWPA
            x_taper_connection = x_size_jj - spacing_jj/2 # x size of the taper connecting the end of the arm to the beginning of the TWPA
            x_connection = x_taper_connection # x dimension of the small square to fill the rightmost unit cell of the TWPA
            y_connection = 2*y_size_jj # y dimension of the small square to fill the rightmost unit cell of the TWPA
        elif self.device == 'LH':
            y_taper_connection = 2*y_size_capa # y size of the taper connecting the end of the arm to the beginning of the TWPA
            x_taper_connection = x_size_capa - spacing_capa/2
            x_connection = x_taper_connection # x dimension of the small square to fill the rightmost unit cell of the TWPA
            y_connection = y_taper_connection # y dimension of the small square to fill the rightmost unit cell of the TWPA
        elif self.device == 'SJ':
            y_taper_connection = 2*y_size_jj # y size of the taper connecting the end of the arm to the beginning of the TWPA
            x_taper_connection = x_size_jj # x size of the taper connecting the end of the arm to the beginning of the TWPA

        elif self.device == 'SNAIL':
            y_taper_connection = y_size_jj # y size of the taper connecting the end of the arm to the beginning of the TWPA
            x_taper_connection = unit_cell_size # x size of the taper connecting the end of the arm to the beginning of the TWPA


        Pad_inst = Pad()
        Pad_inst.x_pad = x_pad
        Pad_inst.y_pad = y_pad
        Pad_inst.taper_length = taper_length
        Pad_inst.x_pad_gap = x_pad_gap
        Pad_inst.y_pad_gap = y_pad_gap

        if self.device in ('RH','LH'):


            total_length = (n_unit_cells-1)*unit_cell_size + x_size_of_cell_tot 
            
            Pad_inst.x_arm = grid_size_um[0]/2 - total_length/2 - (Pad_inst.x_pad_gap + Pad_inst.x_pad + Pad_inst.taper_length) - 1*x_taper_connection # Size of the right and left arm to center the TWPA
            
            """ If bugs in connection of array with pads on right side comment the above line and uncomment the one below"""

            # Pad_inst.x_arm = grid_size_um[0]/2 - chain_length/2 - (Pad_inst.x_pad_gap + Pad_inst.x_pad + Pad_inst.taper_length) - 1.5*x_taper_connection

        elif self.device in ('SJ','SNAIL'):
            Pad_inst.x_arm = grid_size_um[0]/2 - chain_length/2 - (Pad_inst.x_pad_gap + Pad_inst.x_pad + Pad_inst.taper_length) - 1*x_taper_connection # Size of the right and left arm to center the TWPA
        
        Pad_inst.y_arm = y_arm
        Pad_inst.arm_gap = arm_gap
        Pad_inst.pad_layer = pad_bottom_layer
        Pad_inst.arm_layer = connection_wire_bottom_layer
        Pad_inst.ground_layer = ground_layer
        Pad_inst.CPW = True
        Pad_inst.Exclude_ground = False
        pad = Pad_inst.GeneratePad()

        pad_ref_left = gdstk.Reference(pad, origin=(0,grid_size_um[1]/2), rotation=0) # Generates the 1st tapered pad (for bounding) plus the horizontal rectangle "arm"
        pad_ref_right = gdstk.Reference(pad, origin=(grid_size_um[0],grid_size_um[1]/2), rotation=np.pi) # Generates the 1st tapered pad (for bounding) plus the horizontal rectangle "arm"
        cell.add(pad_ref_left,pad_ref_right)
        end_position_pad = Pad_inst.x_size_of_Pad

        ### Add connection
        points_connection = [  (0,-y_arm/2), # Upper point
                                (x_taper_connection, -y_taper_connection/2), # Ends at x = x_taper_connection, y = y_taper_connection
                                (x_taper_connection, y_taper_connection/2), # Ends at x = x_taper_connection, y = y_taper_connection
                                (0,y_arm/2)] # Lower point
        connection = gdstk.Polygon(points_connection, layer=bottom_layer) # Generates the left taper between end of arm and beginning of the TWPA
        cell.add(connection.copy().translate(end_position_pad,grid_size_um[1]/2))

        ### Add TWPA chain
        start_position_chain = end_position_pad + x_taper_connection

        chain = self.generate_chains(n_unit_cells,chain_type='device')
        ref_chain = gdstk.Reference(chain, origin=(start_position_chain,0.5*grid_size_um[1]),rotation=0)
        cell.add(ref_chain)
        end_position_chain = start_position_chain + chain_length

        ### Add connection right

        if self.device in ('RH','LH'):

            connection_right = gdstk.rectangle((0,-y_connection/2), (x_connection,y_connection/2), layer=bottom_layer) # Adds a connction between the end of the TWPA and the right taper
        
            cell.add(connection_right.copy().translate(end_position_chain,grid_size_um[1]/2))

            end_position_chain += x_connection


        # cell.add(connection.copy().rotate(np.pi).translate(end_position_chain + 2*x_taper_connection,grid_size_um[1]/2)) # Places the right taper connecting the end of the TWPA to the right arm
        cell.add(connection.copy().rotate(np.pi).translate(end_position_chain + x_taper_connection,grid_size_um[1]/2))
        end_position_taper = end_position_chain + x_taper_connection

        ### Add ground
        if self.device == 'RH':
            y_ground = 2*unit_cell_height - 2*(x_size_capa - spacing_capa/2)
            x_ground = x_size_jj
        elif self.device == 'LH':
            y_ground = abs(2*unit_cell_height) - 2*(x_size_jj - spacing_jj/2) - litho_overlap
            x_ground = chain_length + x_taper_connection
        elif self.device in ('SJ','SNAIL'):
            y_ground = unit_cell_height
            x_ground = spacing_jj/2


        ### USELESS IT SEEMS

        ground = gdstk.rectangle((0,-y_ground/2), (x_ground,y_ground/2), layer=ground_layer)
        ground.translate(start_position_chain,grid_size_um[1]/2)

        cell.add(ground)

        ### END USELESS STUFF

        ### Add connections ground
        points_connection_ground = [(0,-y_arm/2-arm_gap), 
                                    (x_taper_connection, -y_ground/2),
                                    (x_taper_connection, y_ground/2),
                                    (0,y_arm/2+arm_gap)]

        connection_ground = gdstk.Polygon(points_connection_ground, layer=self.ground_layer) # The left taper for CPW gap opening
        cell.add(connection_ground.copy().translate(end_position_pad,grid_size_um[1]/2))

        cell.add(connection_ground.copy().rotate(np.pi).translate(end_position_chain+x_taper_connection,grid_size_um[1]/2)) # The right taper for CPW gap opening


        ### Add test chains JJs
        if self.generate_test_chains_jj:
            x_TC = self.x_TC_jj
            y_TC = self.y_TC_jj
            TC_block = self.generate_TC_block('jj')
            ref_TC_block = gdstk.Reference(TC_block,origin=(x_TC,y_TC),rotation=0)
            cell.add(ref_TC_block)

        if self.generate_test_chains_SNAIL:

            x_TC_small = self.x_TC_jj
            y_TC_small = self.y_TC_jj
            TC_block = self.generate_TC_block('jj_small')
            ref_TC_block_small = gdstk.Reference(TC_block,origin=(x_TC_small,y_TC_small),rotation=0)
            cell.add(ref_TC_block_small)

            x_TC_large = self.x_TC_jj
            y_TC_large= self.y_TC_jj
            TC_block = self.generate_TC_block('jj_large')
            ref_TC_block_large = gdstk.Reference(TC_block,origin=(x_TC_large,y_TC_large),rotation=0)
            cell.add(ref_TC_block_large)

        ### Add test chains PPCs
        if self.generate_test_chains_capa:
            x_TC = self.x_TC_capa
            y_TC = self.y_TC_capa
            TC_block = self.generate_TC_block('capa')
            ref_TC_block = gdstk.Reference(TC_block,origin=(x_TC,y_TC),rotation=0)
            cell.add(ref_TC_block)

        ### Add label
        if self.add_label:
            x_TC = self.x_chip_label + self.label_shift
            y_TC = self.y_cumulative  + self.label_shift
            info_label = gdstk.text(self.dev_label, self.text_size, (x_TC,y_TC), layer=self.ground_layer)
            cell.add(*info_label)  
            self.y_cumulative  += self.text_size+2*self.label_shift

        ### Add wafer label
        if self.add_wafer_label:
            info_label = gdstk.text(self.wafer_label, self.text_size, (self.x_wafer_label,self.y_wafer_label), layer=self.markers_layer)
            cell.add(*info_label)

        ### Add logo
        if self.add_logo_CNRS:
            logo_CNRS = self.generate_logo_CNRS()
            ref_logo_CNRS = gdstk.Reference(logo_CNRS,origin=(self.x_logo_CNRS,self.y_logo),rotation=0)
            cell.add(ref_logo_CNRS)

        if self.add_logo_Neel:
            logo_Neel = self.generate_logo_Neel()
            ref_logo_Neel = gdstk.Reference(logo_Neel,origin=(self.x_logo_Neel,self.y_logo),rotation=0)
            cell.add(ref_logo_Neel)
            
        ### Add R4t measurements of Al films
        if self.add_R4t_Al:
            R4t_Al = self.generate_R4t_Al()
            ref_R4t_Al = gdstk.Reference(R4t_Al,origin=(self.x_R4t,self.y_R4t),rotation=0)
            cell.add(ref_R4t_Al)

        ### Add test for characterization of wet etching
        if self.add_wet_etching_test:
            wet_etching_block = self.generate_wet_etching_test()
            ref_wet_etching_block = gdstk.Reference(wet_etching_block,origin=(self.x_WET,self.y_WET),rotation=0)
            cell.add(ref_wet_etching_block)

        ### Move cell in order to center markers in the center of a mean field square
        cell_save_ref = gdstk.Reference(cell,origin=(write_field_um/2,write_field_um/2),rotation=0)
        cell_save.add(cell_save_ref)

        cell_save.flatten()

        cell_merged = self.merge_object_per_layer(cell_save, 'all')

        ### Save the layout
        lib.add(cell_merged)
        lib.write_gds(save_location)


    def generate_RES_GDS(self, **kwargs):

        save_location = self.save_location

        lib = gdstk.Library()
        cell_save = gdstk.Cell("cell_out")
        cell = gdstk.Cell("cell")
        cell_tmp = gdstk.Cell("LER_tmp")

        grid_size = self.grid_size
        write_field = self.write_field
        alignment_marker_size_um = self.alignment_marker_size_um
        write_field_um = write_field*1000
        grid_size_um = (grid_size[0]*1000,grid_size[1]*1000)

        feedline = self.feedline
        feedline_width = self.feedline_width
        resonators_chip_edge_spacing = self.resonators_chip_edge_spacing
        resonators_coupling_gap = self.resonators_coupling_gap

        unit_cell = self.unit_cell
        unit_cell_size = self.unit_cell_size
        n_unit_cells = int(self.n_unit_cells/self.cells_in_element)

        dicing_gap = self.dicing_gap

        current_position = np.array([dicing_gap,0.5*grid_size_um[1]])

        ### Add markers
        markers = self.generate_markers()
        markers_ref = gdstk.Reference(markers, origin=(0,0))
        cell.add(markers_ref)

        ### Add Feedline
        feedline_ref = gdstk.Reference(feedline, origin=current_position)
        cell_tmp.add(feedline_ref)

        ### Add resonators
        resonators_x_offset = np.linspace(resonators_chip_edge_spacing + unit_cell_size, grid_size_um[0] - resonators_chip_edge_spacing - unit_cell_size, n_unit_cells)
        resonators_y_offset = feedline_width/2 + resonators_coupling_gap

        for i in range(n_unit_cells):
            current_position[0] =  resonators_x_offset[i]

            if i%2 == 0:
                current_position[1] = 0.5*grid_size_um[1]+resonators_y_offset[i]
                resonator_ref = gdstk.Reference(unit_cell[i], origin=current_position, rotation=np.pi)
            else:
                current_position[1] = 0.5*grid_size_um[1]-resonators_y_offset[i]
                resonator_ref = gdstk.Reference(unit_cell[i], origin=current_position)

            cell_tmp.add(resonator_ref)

        LERs_ref = gdstk.Reference(cell_tmp, origin=(0,0))
        cell.add(LERs_ref)

        ### Add label
        if self.add_label:
            x_TC = self.x_chip_label + self.label_shift
            y_TC = self.y_cumulative  + self.label_shift

            info_label = gdstk.text(self.dev_label, self.text_size, (x_TC,y_TC), layer=self.ground_layer)
            cell.add(*info_label)  

            self.y_cumulative  += self.text_size+2*self.label_shift

        ### Add wafer label
        if self.add_wafer_label:
            info_label = gdstk.text(self.wafer_label, self.text_size, (self.x_wafer_label,self.y_wafer_label), layer=self.markers_layer)
            cell.add(*info_label)

        ### Add logo
        if self.add_logo_CNRS:
            logo_CNRS = self.generate_logo_CNRS()
            ref_logo_CNRS = gdstk.Reference(logo_CNRS,origin=(self.x_logo_CNRS,self.y_logo),rotation=0)
            cell.add(ref_logo_CNRS)

        if self.add_logo_Neel:
            logo_Neel = self.generate_logo_Neel()
            ref_logo_Neel = gdstk.Reference(logo_Neel,origin=(self.x_logo_Neel,self.y_logo),rotation=0)
            cell.add(ref_logo_Neel)
            
        ### Add R4t measurements of Al films
        if self.add_R4t_Al:
            R4t_Al = self.generate_R4t_Al(Exclude_ground=True)
            ref_R4t_Al = gdstk.Reference(R4t_Al,origin=(self.x_R4t,self.y_R4t),rotation=0)
            cell.add(ref_R4t_Al)

        ### Add test for characterization of wet etching
        if self.add_wet_etching_test:
            wet_etching_block = self.generate_wet_etching_test()
            ref_wet_etching_block = gdstk.Reference(wet_etching_block,origin=(self.x_WET,self.y_WET),rotation=0)
            cell.add(ref_wet_etching_block)

        ### Move cell in order to center markers in the center of a mean field square
        cell_save_ref = gdstk.Reference(cell,origin=(write_field_um/2,write_field_um/2),rotation=0)
        cell_save.add(cell_save_ref)

        cell_save.flatten()

        cell_merged = self.merge_object_per_layer(cell_save, 'all')

        ### Save the layout
        lib.add(cell_merged)
        lib.write_gds(save_location)

    def generate_TWPA_GDS_inv_microstrip_pad(self):

        save_location = self.save_location

        lib = gdstk.Library()
        cell_save = gdstk.Cell("TWPA")
        cell = gdstk.Cell("TWPA_tmp")

        grid_size = self.grid_size
        write_field = self.write_field
        alignment_marker_size_um = self.alignment_marker_size_um
        write_field_um = write_field*1000
        grid_size_um = (grid_size[0]*1000,grid_size[1]*1000)
              

        unit_cell = self.unit_cell
        unit_cell_size = self.unit_cell_size
        unit_cell_height = self.unit_cell_height
        n_unit_cells = int(self.n_unit_cells/self.cells_in_element)
        x_size_jj = self.x_size_jj
        y_size_jj = self.y_size_jj
        x_size_capa = self.x_size_capa
        y_size_capa = self.y_size_capa
        spacing_jj = self.spacing_jj
        spacing_capa = self.spacing_capa

        if self.device in ('RH','LH'):

            x_size_of_cell_tot = self.unit_cell_size_tot

        litho_overlap = self.litho_overlap

        ground_layer = self.ground_layer
        pad_bottom_layer = self.pad_bottom_layer
        connection_wire_bottom_layer = self.connection_wire_bottom_layer
        if self.device in ('RH', 'SJ','SNAIL'):
            bottom_layer = self.jj_bottom_layer
        elif self.device == 'LH':
            bottom_layer = self.capa_bottom_layer

        ### Add markers
        markers = self.generate_markers()
        markers_ref = gdstk.Reference(markers, origin=(0,0))
        cell.add(markers_ref)

        ### Compute length of the chain
        chain_length = unit_cell_size*n_unit_cells

        ### Add bonding pads 
        if self.device == 'RH':
            y_taper_connection = 2*y_size_jj + 2*x_size_capa - spacing_capa # y size of the taper connecting the end of the arm to the beginning of the TWPA
            x_taper_connection = x_size_jj - spacing_jj/2 # x size of the taper connecting the end of the arm to the beginning of the TWPA
            x_connection = x_taper_connection # x dimension of the small square to fill the rightmost unit cell of the TWPA
            y_connection = 2*y_size_jj # y dimension of the small square to fill the rightmost unit cell of the TWPA
        elif self.device == 'LH':
            y_taper_connection = 2*y_size_capa # y size of the taper connecting the end of the arm to the beginning of the TWPA
            x_taper_connection = x_size_capa - spacing_capa/2
            x_connection = x_taper_connection # x dimension of the small square to fill the rightmost unit cell of the TWPA
            y_connection = y_taper_connection # y dimension of the small square to fill the rightmost unit cell of the TWPA
        elif self.device == 'SJ':
            y_taper_connection = 2*y_size_jj # y size of the taper connecting the end of the arm to the beginning of the TWPA
            x_taper_connection = x_size_jj # x size of the taper connecting the end of the arm to the beginning of the TWPA
        elif self.device == 'SNAIL':
            y_taper_connection = y_size_jj # y size of the taper connecting the end of the arm to the beginning of the TWPA
            x_taper_connection = unit_cell_size # x size of the taper connecting the end of the arm to the beginning of the TWPA


        Pad_inst = Pad_TWPA_inv_microstrip()
        Pad_inst.bonding_pad_width = self.y_pad_inv
        Pad_inst.bonding_pad_length = self.x_pad_inv
        Pad_inst.bonding_pad_gap_x = self.x_pad_inv_gap
        Pad_inst.bonding_pad_gap_y = self.y_pad_inv_gap
        Pad_inst.x_dice_gap = self.x_pad_gap
        # Pad_inst.connecting_line_length = self.x_connecting_line
        Pad_inst.connecting_line_width = self.y_connecting_line
        Pad_inst.connecting_wire_gap = self.connecting_line_gap
        Pad_inst.pad_wire_overlap = self.pad_line_overlap
        Pad_inst.capacitance_along_connecting_wire_width = self.capacitance_along_connecting_line_width
        Pad_inst.capacitance_along_connecting_wire_pitch_first = self.capacitance_along_connecting_line_pitch_first
        Pad_inst.capacitance_along_connecting_wire_pitch = self.capacitance_along_connecting_line_pitch
        Pad_inst.layer_1 = pad_bottom_layer
        Pad_inst.layer_2 = connection_wire_bottom_layer
        Pad_inst.layer_ground = ground_layer


        if self.device in ('RH','LH'):


            total_length = (n_unit_cells-1)*unit_cell_size + x_size_of_cell_tot 
            
             
            Pad_inst.connecting_line_length = grid_size_um[0]/2 - total_length/2 - (Pad_inst.bonding_pad_length + Pad_inst.x_dice_gap) # Size of the right and left arm to center the TWPA

        elif self.device in ('SJ','SNAIL'):

            Pad_inst.connecting_line_length = grid_size_um[0]/2 - chain_length/2 - (Pad_inst.bonding_pad_length + Pad_inst.x_dice_gap) # Size of the right and left arm to center the TWPA
        
        pad = Pad_inst.Generate_Pad_TWPA()
        pad_ref_left = gdstk.Reference(pad, origin=(0,grid_size_um[1]/2), rotation=0) # Generates the 1st tapered pad (for bounding) plus the horizontal rectangle "arm"
        pad_ref_right = gdstk.Reference(pad, origin=(grid_size_um[0],grid_size_um[1]/2), rotation=np.pi) # Generates the 1st tapered pad (for bounding) plus the horizontal rectangle "arm"
        cell.add(pad_ref_left,pad_ref_right)
        end_position_pad = Pad_inst.x_size_of_Pad_inv

        ### Add TWPA chain
        start_position_chain = end_position_pad

        chain = self.generate_chains(n_unit_cells,chain_type='device')
        ref_chain = gdstk.Reference(chain, origin=(start_position_chain,0.5*grid_size_um[1]),rotation=0)
        cell.add(ref_chain)
        end_position_chain = start_position_chain + chain_length

        ### Add connection right

        if self.device in ('RH','LH'):

            connection_right = gdstk.rectangle((0,-y_connection/2), (x_connection,y_connection/2), layer=bottom_layer) # Adds a connction between the end of the TWPA and the right taper
        
            cell.add(connection_right.copy().translate(end_position_chain,grid_size_um[1]/2))

            end_position_chain += x_connection

        ### Add ground
        if self.device == 'RH':
            y_ground = 2*unit_cell_height - 2*(x_size_capa - spacing_capa/2)
            x_ground = x_size_jj
        elif self.device == 'LH':
            y_ground = abs(2*unit_cell_height) - 2*(x_size_jj - spacing_jj/2) - litho_overlap
            x_ground = chain_length + x_taper_connection
        elif self.device in ('SJ','SNAIL'):
            y_ground = unit_cell_height
            x_ground = spacing_jj/2


        ### USELESS IT SEEMS

        ground = gdstk.rectangle((0,-y_ground/2), (x_ground,y_ground/2), layer=ground_layer)
        ground.translate(start_position_chain,grid_size_um[1]/2)

        cell.add(ground)

        ### END USELESS STUFF

        ### Add test chains JJs
        if self.generate_test_chains_jj:
            x_TC = self.x_TC_jj
            y_TC = self.y_TC_jj
            TC_block = self.generate_TC_block('jj')
            ref_TC_block = gdstk.Reference(TC_block,origin=(x_TC,y_TC),rotation=0)
            cell.add(ref_TC_block)

        if self.generate_test_chains_SNAIL:

            x_TC_small = self.x_TC_jj
            y_TC_small = self.y_TC_jj
            TC_block = self.generate_TC_block('jj_small')
            ref_TC_block_small = gdstk.Reference(TC_block,origin=(x_TC_small,y_TC_small),rotation=0)
            cell.add(ref_TC_block_small)

            x_TC_large = self.x_TC_jj
            y_TC_large= self.y_TC_jj
            TC_block = self.generate_TC_block('jj_large')
            ref_TC_block_large = gdstk.Reference(TC_block,origin=(x_TC_large,y_TC_large),rotation=0)
            cell.add(ref_TC_block_large)

        ### Add test chains PPCs
        if self.generate_test_chains_capa:
            x_TC = self.x_TC_capa
            y_TC = self.y_TC_capa
            TC_block = self.generate_TC_block('capa')
            ref_TC_block = gdstk.Reference(TC_block,origin=(x_TC,y_TC),rotation=0)
            cell.add(ref_TC_block)

        ### Add label
        if self.add_label:
            x_TC = self.x_chip_label + self.label_shift
            y_TC = self.y_cumulative  + self.label_shift
            info_label = gdstk.text(self.dev_label, self.text_size, (x_TC,y_TC), layer=self.ground_layer)
            cell.add(*info_label)  
            self.y_cumulative  += self.text_size+2*self.label_shift

        ### Add wafer label
        if self.add_wafer_label:
            info_label = gdstk.text(self.wafer_label, self.text_size, (self.x_wafer_label,self.y_wafer_label), layer=self.markers_layer)
            cell.add(*info_label)

        ### Add logo
        if self.add_logo_CNRS:
            logo_CNRS = self.generate_logo_CNRS()
            ref_logo_CNRS = gdstk.Reference(logo_CNRS,origin=(self.x_logo_CNRS,self.y_logo),rotation=0)
            cell.add(ref_logo_CNRS)

        if self.add_logo_Neel:
            logo_Neel = self.generate_logo_Neel()
            ref_logo_Neel = gdstk.Reference(logo_Neel,origin=(self.x_logo_Neel,self.y_logo),rotation=0)
            cell.add(ref_logo_Neel)
            
        ### Add R4t measurements of Al films
        if self.add_R4t_Al:
            R4t_Al = self.generate_R4t_Al()
            ref_R4t_Al = gdstk.Reference(R4t_Al,origin=(self.x_R4t,self.y_R4t),rotation=0)
            cell.add(ref_R4t_Al)

        ### Add test for characterization of wet etching
        if self.add_wet_etching_test:
            wet_etching_block = self.generate_wet_etching_test()
            ref_wet_etching_block = gdstk.Reference(wet_etching_block,origin=(self.x_WET,self.y_WET),rotation=0)
            cell.add(ref_wet_etching_block)

        ### Move cell in order to center markers in the center of a mean field square
        cell_save_ref = gdstk.Reference(cell,origin=(write_field_um/2,write_field_um/2),rotation=0)
        cell_save.add(cell_save_ref)

        cell_save.flatten()

        cell_merged = self.merge_object_per_layer(cell_save, 'all')

        ### Save the layout
        lib.add(cell_merged)
        lib.write_gds(save_location)
