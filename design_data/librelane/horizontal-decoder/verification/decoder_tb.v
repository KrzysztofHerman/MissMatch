
`timescale 1ns/1ps

module decoder_tb;

    // ------------------------------------------------------------------
    // Timing (simple integer delay to avoid real→time casts)
    // ------------------------------------------------------------------
    // Treat this as "sample period" between vectors.
    parameter integer DT_NS = 100;   // 100 ns per step (adjust as you like)

    // DUT parameters
    parameter integer NBITS = 8;   // 100 ns per step (adjust as you like)
    // ------------------------------------------------------------------
    // DUT connections
    // ------------------------------------------------------------------
    reg        ena_i;
    reg  [NBITS-1:0] input_ni;
    wire [2**NBITS-1:0] output_o;
    wire [2**NBITS-1:0] output_no;

    decoder dut (
        .ena_i      (ena_i),
        .input_ni  (input_ni),
        .output_no (output_no),
        .output_o  (output_o)
    );

    // ------------------------------------------------------------------
    // Expected-value helper (Verilog-2005 style)
    // ------------------------------------------------------------------
    function [2**NBITS-1:0] expected_o;
        input       ena;
        input [NBITS-1:0] in_ni;
        integer idx;
        begin
           idx = (~in_ni) & ((1 << NBITS) - 1); 

        if (ena)
            expected_o = (1 << idx);       // One-hot output
        else
            expected_o = 0;
            // Decoder spec: internally ~input_ni is decoded one-hot when enabled
          //  idx = (~in_ni) & 3'b111;           
           // if (ena)
             //   expected_o = (8'b1 << idx);
            //else
              //  expected_o = 0;
        end
    endfunction

    // ------------------------------------------------------------------
    // Stimulus + checks
    // ------------------------------------------------------------------
    integer i;
    integer errors;

    initial begin
        errors   = 0;
        ena_i     = 1'b0;
        input_ni = 0;

        // optional dump from TB (decoder may also dump)
        $dumpfile("decoder_tb.vcd");
        $dumpvars(0, decoder_tb);

        $display(" time[ns] | en | in_ni | ~in |   expected_o |    output_o | expected_no |   output_no | result");
        $display("---------------------------------------------------------------------------------------------------");

        // Let signals settle then enable
        #(DT_NS);
        ena_i = 1'b1;

        // Walk through all 8 input codes
        for (i = 0; i < 2**NBITS; i = i + 1) begin
            input_ni = i[NBITS-1:0];
            #(DT_NS/2);  // give combinational logic time

            check_vector();

            #(DT_NS/2);
        end

        // Check one disabled case
        ena_i = 1'b0;
        input_ni = 3;
        #(DT_NS/2);
        check_vector();
        #(DT_NS/2);

        if (errors == 0)
            $display("All checks PASSED.");
        else
            $display("TEST FAILED with %0d error(s).", errors);

        $finish;
    end

    // Simple checker (no SystemVerilog $fatal/$error)
    task check_vector;
        reg [2**NBITS-1:0] exp_o, exp_no;
        reg [NBITS-1:0] inv_idx;
        begin
            inv_idx = (~input_ni) & 1;
            exp_o   = expected_o(ena_i, input_ni);
            exp_no  = ~exp_o;

            if (output_o !== exp_o || output_no !== exp_no) begin
                $display("%8t |  %0b |  %0x8h |  %08h  |     %08b |     %08b |    %08b |    %08b | FAIL",
                         $time, ena_i, input_ni, inv_idx, exp_o, output_o, exp_no, output_no);
                errors = errors + 1;
            end else begin
                $display("%8t |  %0b |  0x%x |  0x%x  |     0x%x |     0x%x |    0x%x |   0x%x | PASS",
                         $time, ena_i, input_ni, inv_idx, exp_o, output_o, exp_no, output_no);
            end
        end
    endtask

endmodule
