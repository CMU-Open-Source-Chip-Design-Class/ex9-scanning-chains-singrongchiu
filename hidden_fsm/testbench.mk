TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(shell pwd)/hidden_fsm_out.sv
TOPLEVEL = hidden_fsm
MODULE = testbench
SIM = verilator
EXTRA_ARGS += --trace --trace-structs -Wno-fatal
include $(shell cocotb-config --makefiles)/Makefile.sim
