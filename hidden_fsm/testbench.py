import os
import logging
import cocotb
from cocotb.clock import Timer
from cocotb.triggers import *

# Make sure to set FILE_NAME
# to the filepath of the .log
# file you are working with
CHAIN_LENGTH = 3 # need to change for each design
FILE_NAME    = "hidden_fsm.log"



# Holds information about a register
# in your design.

################
# DO NOT EDIT!!!
################
class Register:

    def __init__(self, name) -> None:
        self.name = name            # Name of register, as in .log file
        self.size = -1              # Number of bits in register

        self.bit_list = list()      # Set this to the register's contents, if you want to
        self.index_list = list()    # List of bit mappings into chain. See handout

        self.first = -1             # LSB mapping into scan chain
        self.last  = -1             # MSB mapping into scan chain


# Holds information about the scan chain
# in your design.
        
################
# DO NOT EDIT!!!
################
class ScanChain:

    def __init__(self) -> None:
        self.registers = dict()     # Dictionary of Register objects, indexed by 
                                    # register name
        
        self.chain_length = 0       # Number of FFs in chain


# Sets up a new ScanChain object
# and returns it

################     
# DO NOT EDIT!!!
################
def setup_chain(filename):

    scan_chain = ScanChain()

    f = open(filename, "r")
    for line in f:
        linelist = line.split()
        index, name, bit = linelist[0], linelist[1], linelist[2]

        if name not in scan_chain.registers:
            reg = Register(name)
            reg.index_list.append((int(bit), int(index)))
            scan_chain.registers[name] = reg

        else:
            scan_chain.registers[name].index_list.append((int(bit), int(index)))
        
    f.close()

    for name in scan_chain.registers:
        cur_reg = scan_chain.registers[name]
        cur_reg.index_list.sort()
        new_list = list()
        for tuple in cur_reg.index_list:
            new_list.append(tuple[1])
        
        cur_reg.index_list = new_list
        cur_reg.bit_list   = [0] * len(new_list)
        cur_reg.size = len(new_list)
        cur_reg.first = new_list[0]
        cur_reg.last  = new_list[-1]
        scan_chain.chain_length += len(cur_reg.index_list)

    return scan_chain


# Prints info of given Register object

################
# DO NOT EDIT!!!
################
def print_register(reg):
    print("------------------")
    print(f"NAME:    {reg.name}")
    print(f"BITS:    {reg.bit_list}")
    print(f"INDICES: {reg.index_list}")
    print("------------------")


# Prints info of given ScanChain object

################   
# DO NOT EDIT!!!
################
def print_chain(chain):
    print("---CHAIN DISPLAY---\n")
    print(f"CHAIN SIZE: {chain.chain_length}\n")
    print("REGISTERS: \n")
    for name in chain.registers:
        cur_reg = chain.registers[name]
        print_register(cur_reg)



#-------------------------------------------------------------------

# This function steps the clock once.
    
# Hint: Use the Timer() builtin function
async def step_clock(dut):

    ######################
    # TODO: YOUR CODE HERE 
    ######################
    
    dut.clk.value = 1
    await Timer(10, units='ns')
    dut.clk.value = 0
    await Timer(10, units='ns')
    
    return
    

#-------------------------------------------------------------------

# This function places a bit value inside FF of specified index.
        
# Hint: How many clocks would it take for value to reach
#       the specified FF?
        
async def input_chain_single(dut, bit, ff_index):

    ######################
    # TODO: YOUR CODE HERE 
    ######################
    
    # ff is 0-indexed
    
    dut.scan_en.value = 1
    dut.scan_in.value = bit
    await step_clock(dut)
    
    for i in range(ff_index):
      await step_clock(dut)
      
    dut.scan_en.value = 0
      
    return
    
#-------------------------------------------------------------------

# This function places multiple bit values inside FFs of specified indexes.
# This is an upgrade of input_chain_single() and should be accomplished
#   for Part H of Task 1
        
# Hint: How many clocks would it take for value to reach
#       the specified FF?
        
async def input_chain(dut, bit_list, ff_index):

    ######################
    # TODO: YOUR CODE HERE 
    ######################
    
    '''
    dut.scan_in.value = bit_list[0]
    await step_clock(dut)
    bit_list = bit_list[1:]
    '''
    
    dut.scan_en.value = 1
    for i in range(len(bit_list)):
      dut.scan_in.value = bit_list[0]
      await step_clock(dut)
      # print(f"bit_list[0]: {bit_list[0]}")
      bit_list = bit_list[1:]
    
    for i in range(ff_index):
      await step_clock(dut)
    dut.scan_en.value = 0
      
    return

#-----------------------------------------------

# This function retrieves a single bit value from the
# chain at specified index 
        
async def output_chain_single(dut, ff_index):

    ######################
    # TODO: YOUR CODE HERE 
    ######################
    output = 0
    
    dut.scan_en.value = 1
    for i in range(CHAIN_LENGTH - ff_index):
      output = (output << 1) + dut.scan_out.value
      await step_clock(dut)
    dut.scan_en.value = 0
    
    return output       

#-----------------------------------------------

# This function retrieves a single bit value from the
# chain at specified index
# This is an upgrade of input_chain_single() and should be accomplished
#   for Part H of Task 1
        
async def output_chain(dut, ff_index, output_length):

    ######################
    # TODO: YOUR CODE HERE 
    ######################
    
    output = 0
    
    dut.scan_en.value = 1
    for i in range(CHAIN_LENGTH - (ff_index + output_length)):
      await step_clock(dut)
    
    for i in range(output_length): 
      output = (output << 1) + dut.scan_out.value
      await step_clock(dut)
    dut.scan_en.value = 0
    
    return output

#-----------------------------------------------

# Your main testbench function

@cocotb.test()
async def test000(dut):

    global CHAIN_LENGTH
    global FILE_NAME        # Make sure to edit this guy
                            # at the top of the file

    # Setup the scan chain object
    chain = setup_chain(FILE_NAME)
    bit_list = [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]]

    for i in range(8): 
      print(f'===== CURRENT STATE: {bit_list[i]} ===== ')
      await (input_chain(dut, bit_list[i], 0))
    
      dut.data_avail.value = 0
      await step_clock(dut)
      print(f"clk {dut.clk.value} data_avail {dut.data_avail.value}")
      print(f"buf_en {dut.buf_en.value} out_sel {dut.out_sel.value} out_writing {dut.out_writing.value}")
      outval = await (output_chain(dut, 0, 3))
      print(f'next state: {outval}')
      print()
    
      dut.data_avail.value = 1
      await step_clock(dut)
      print(f"clk {dut.clk.value} data_avail {dut.data_avail.value}")
      print(f"buf_en {dut.buf_en.value} out_sel {dut.out_sel.value} out_writing {dut.out_writing.value}")
      outval = await (output_chain(dut, 0, 3))
      print(f'next state: {outval}')
      print()
    
    assert True

# @cocotb.test()
async def basic_test(dut):
    print("============== STARTING TEST 1 ==============")

    # Run the clock
    # cocotb.start_soon(Clock(dut.clock, 10, units="ns").start())
    
    dut.clk.value = 0
    dut.data_avail.value = 0
    await Timer(2, units='ns')
    print(f"clk {dut.clk.value} data_avail {dut.data_avail.value}")
    print(f"buf_en {dut.buf_en.value} out_sel {dut.out_sel.value} out_writing {dut.out_writing.value}")
    print()
    
    dut.clk.value = 0
    dut.data_avail.value = 1
    await Timer(2, units='ns')
    print(f"clk {dut.clk.value} data_avail {dut.data_avail.value}")
    print(f"buf_en {dut.buf_en.value} out_sel {dut.out_sel.value} out_writing {dut.out_writing.value}")
    print()
    
    dut.clk.value = 1
    dut.data_avail.value = 0
    await Timer(2, units='ns')
    print(f"clk {dut.clk.value} data_avail {dut.data_avail.value}")
    print(f"buf_en {dut.buf_en.value} out_sel {dut.out_sel.value} out_writing {dut.out_writing.value}")
    print()
    
    dut.clk.value = 1
    dut.data_avail.value = 1
    await Timer(2, units='ns')
    print(f"clk {dut.clk.value} data_avail {dut.data_avail.value}")
    print(f"buf_en {dut.buf_en.value} out_sel {dut.out_sel.value} out_writing {dut.out_writing.value}")
    print()
    
    dut.clk.value = 0
    dut.data_avail.value = 0
    await Timer(2, units='ns')
    print(f"clk {dut.clk.value} data_avail {dut.data_avail.value}")
    print(f"buf_en {dut.buf_en.value} out_sel {dut.out_sel.value} out_writing {dut.out_writing.value}")
    print()
    
    dut.clk.value = 1
    dut.data_avail.value = 0
    await Timer(2, units='ns')
    print(f"clk {dut.clk.value} data_avail {dut.data_avail.value}")
    print(f"buf_en {dut.buf_en.value} out_sel {dut.out_sel.value} out_writing {dut.out_writing.value}")
    print()
    
    dut.clk.value = 0
    dut.data_avail.value = 0
    await Timer(2, units='ns')
    print(f"clk {dut.clk.value} data_avail {dut.data_avail.value}")
    print(f"buf_en {dut.buf_en.value} out_sel {dut.out_sel.value} out_writing {dut.out_writing.value}")
    print()
    
    dut.clk.value = 1
    dut.data_avail.value = 0
    await Timer(2, units='ns')
    print(f"clk {dut.clk.value} data_avail {dut.data_avail.value}")
    print(f"buf_en {dut.buf_en.value} out_sel {dut.out_sel.value} out_writing {dut.out_writing.value}")
    print()
    
    assert True
    
    
