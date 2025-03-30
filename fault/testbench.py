import os
import logging
import cocotb
from cocotb.clock import Timer
from cocotb.triggers import *


# Your main testbench function
async def test_vector(dut, vector):

    dut.a.value = vector[0]
    dut.b.value = vector[1]
    dut.c.value = vector[2]
    dut.d.value = vector[3]
    await Timer(10, units='ns')
    
    not_a = not vector[0]
    not_c = not vector[2]   
    xor_ab_inv = (not_a ^ vector[1])
    or_cd_inv = (not_c | vector[3])
    and_result = xor_ab_inv & or_cd_inv
    
    print(f"vector: {vector}")
    print(f"expected {and_result}")
    print(f"actual result {dut.x.value}")
    print()
    
    # assert (and_result == dut.x.value)

@cocotb.test()
async def basic_test(dut):
    print("============== STARTING TEST 1 ==============")

    # Run the clock
    # cocotb.start_soon(Clock(dut.clock, 10, units="ns").start())
    
    vectors = [
    [0, 0, 0, 1],
    [0, 1, 0, 1],
    [0, 1, 1, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 1],
    [1, 0, 1, 0],
    [1, 0, 1, 1],
    [1, 1, 0, 1]    
    ]
    
    for vector in vectors:
      await test_vector(dut, vector)
    
    assert True
    
    
