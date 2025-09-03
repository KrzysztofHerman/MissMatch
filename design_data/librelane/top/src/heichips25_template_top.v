// SPDX-FileCopyrightText: © 2025 Leo Moser
// SPDX-License-Identifier: Apache-2.0

module top (
    inout  wire [15:0] ui_PAD,
);

    wire [15:0] ui_PAD2CORE;
    wire [127:0] out1;
    wire [127:0] out2;
    wire [127:0] out3;
    wire [127:0] out4;

    // Power/Ground IO pad instances
    
    (* keep *)
    sg13g2_IOPadVdd sg13g2_IOPadVdd_south ();

    (* keep *)
    sg13g2_IOPadVss sg13g2_IOPadVss_south ();

    (* keep *)
    sg13g2_IOPadIOVss sg13g2_IOPadIOVss_north ();

    (* keep *)
    sg13g2_IOPadIOVdd sg13g2_IOPadIOVdd_north ();

    (* keep *)
    sg13g2_IOPadAnalog sg13g2_IOPadAnalog_DrainF ();
    (* keep *)
    sg13g2_IOPadAnalog sg13g2_IOPadAnalog_DrainS ();
    (* keep *)
    sg13g2_IOPadAnalog sg13g2_IOPadAnalog_SourceF ();
    (* keep *)
    sg13g2_IOPadAnalog sg13g2_IOPadAnalog_SourceS ();
    (* keep *)
    sg13g2_IOPadAnalog sg13g2_IOPadAnalog_Gate ();
    (* keep *)
    sg13g2_IOPadAnalog sg13g2_IOPadAnalog_Vcl ();

    (* keep *)
    sg13g2_IOPadAnalog sg13g2_IOPadAnalog_Bulk ();
    



    generate
    for (genvar i=0; i<16; i++) begin : sg13g2_IOPadIn_ui
        sg13g2_IOPadIn ui (
            .p2c (ui_PAD2CORE[i]),
            .pad (ui_PAD[i])
        );
    end
    endgenerate

(* keep *)
vdecoder vdec(
	.ena_i(ui_PAD2CORE[0]),
	.input_ni(ui_PAD2CORE[7:1]),
	.output_o(out1),
	.output_no(out2)
);

(* keep *)
hdecoder hdec(
	.ena_i(ui_PAD2CORE[8]),
	.input_ni(ui_PAD2CORE[15:9]),
	.output_o(out3),
	.output_no(out4)
);


(* keep *)
Drain_Line dl1 (.ctrl_p(out3[0]), .ctrl_n(out4[0]));
(* keep *)
Drain_Line dl2 (.ctrl_p(out3[1]), .ctrl_n(out4[2]));

(* keep *)
matrix mat1 ();
(* keep *)
matrix mat2 ();
(* keep *)
matrix mat3 ();
(* keep *)
matrix mat4 ();
//(* keep *)
//matrix mat5 ();


endmodule


module Drain_Line(input ctrl_p, input ctrl_n);
endmodule 
module matrix();
endmodule 
