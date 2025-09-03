module vdecoder #(
    parameter N_BITS = 7
)(
	input  logic                    ena_i,
	input  logic [N_BITS-1:0]       input_ni,
	output logic [2**N_BITS-1:0]    output_o,
	output logic [2**N_BITS-1:0]    output_no
);
	
	logic [N_BITS-1:0] input_i;
	
	// Invert all bits of the input
	assign input_i = ~input_ni;
	
	// Decode the signal
	always_comb begin
	    for (int i=0; i<2**N_BITS; i++) begin
	        output_o[i] = ~ena_i && (i == input_i);
	    end
	end
	
	// Assign the complementary output
	assign output_no = ~output_o;

endmodule
