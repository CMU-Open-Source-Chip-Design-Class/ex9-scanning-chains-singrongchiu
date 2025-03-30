import copy
import cocotb
from cocotb.triggers import Timer


# Make sure to set FILE_NAME
# to the filepath of the .log
# file you are working with
CHAIN_LENGTH = 13 # need to change for each design
FILE_NAME    = "adder/adder.log"



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
    print(f"first x_out {dut.x_out.value}")
    
    dut.scan_en.value = 1
    for i in range(CHAIN_LENGTH - (ff_index + output_length)):
      await step_clock(dut)
      print(f"x_out {dut.x_out.value}")
    
    for i in range(output_length): 
      output = (output << 1) + dut.scan_out.value
      await step_clock(dut)
    dut.scan_en.value = 0
    
    return output

#-----------------------------------------------

# Your main testbench function

@cocotb.test()
async def test(dut):

    global CHAIN_LENGTH
    global FILE_NAME        # Make sure to edit this guy
                            # at the top of the file

    # Setup the scan chain object
    chain = setup_chain(FILE_NAME)
    
    '''
    print("PRINTING DUT")
    print(dut)
    print("PRINTING CHAIN")
    print(chain.registers)
    for register in chain.registers.items():
      print("chain reg print")
      print(register[1].name)
      print(register[1].index_list)
      print(register[1].size)
    print(chain.chain_length)
    '''
    
    bit_list = [1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0] # adding b = 10 and a = 7, initializing x_out to 0
    # first 4 bits with msb in front - b_reg, next 4 bits - a_reg, last 5 bits - x_out
    await (input_chain(dut, bit_list, 0))
    print(f"after input x_out {dut.x_out.value}")
    
    await step_clock(dut)
    outval = await (output_chain(dut, 0, 5))
    print(f'this is what 14 + 7 is: {outval}')
    assert (outval == 21)
    

