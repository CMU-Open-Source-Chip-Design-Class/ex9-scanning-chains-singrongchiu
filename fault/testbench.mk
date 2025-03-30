TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(shell pwd)/fault5.sv
TOPLEVEL = fault
MODULE = testbench
SIM = verilator
EXTRA_ARGS += --trace --trace-structs -Wno-fatal
include $(shell cocotb-config --makefiles)/Makefile.sim
