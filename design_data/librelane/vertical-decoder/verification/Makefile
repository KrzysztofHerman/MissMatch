# Makefile ─ simple run for tb_flash_adc8_sine

SRC           := vdecoder.nl.v decoder_tb.v sg13g2_stdcell.v

OUT      := decoder_tb.vvp

# Compile step
$(OUT): $(SRC)
	iverilog -g2005-sv -o $@ $(SRC)

# Clean up
clean:
	rm -f $(OUT) *.vcd

.PHONY: all wave clean
