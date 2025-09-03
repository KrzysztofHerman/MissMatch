module decoder (ena_i,
    input_ni,
    output_no,
    output_o);
 input ena_i;
 input [2:0] input_ni;
 output [7:0] output_no;
 output [7:0] output_o;

 wire _00_;
 wire _01_;
 wire _02_;
 wire _03_;
 wire _04_;
 wire _05_;
 wire _06_;
 wire _07_;
 wire _08_;

 sg13g2_nand2_1 _09_ (.Y(_00_),
    .A(input_ni[1]),
    .B(input_ni[0]));
 sg13g2_nand2_1 _10_ (.Y(_01_),
    .A(input_ni[2]),
    .B(ena_i));
 sg13g2_nor2_1 _11_ (.A(_00_),
    .B(_01_),
    .Y(output_o[0]));
 sg13g2_or2_1 _12_ (.X(output_no[0]),
    .B(_01_),
    .A(_00_));
 sg13g2_nor2b_1 _13_ (.A(input_ni[0]),
    .B_N(input_ni[1]),
    .Y(_02_));
 sg13g2_nand2b_1 _14_ (.Y(_03_),
    .B(input_ni[1]),
    .A_N(input_ni[0]));
 sg13g2_nor2_1 _15_ (.A(_01_),
    .B(_03_),
    .Y(output_o[1]));
 sg13g2_nand2b_1 _16_ (.Y(output_no[1]),
    .B(_02_),
    .A_N(_01_));
 sg13g2_nor2b_1 _17_ (.A(input_ni[1]),
    .B_N(input_ni[0]),
    .Y(_04_));
 sg13g2_nand2b_1 _18_ (.Y(_05_),
    .B(input_ni[0]),
    .A_N(input_ni[1]));
 sg13g2_nor2_1 _19_ (.A(_01_),
    .B(_05_),
    .Y(output_o[2]));
 sg13g2_nand2b_1 _20_ (.Y(output_no[2]),
    .B(_04_),
    .A_N(_01_));
 sg13g2_nor2_1 _21_ (.A(input_ni[1]),
    .B(input_ni[0]),
    .Y(_06_));
 sg13g2_nor2b_1 _22_ (.A(_01_),
    .B_N(_06_),
    .Y(output_o[3]));
 sg13g2_nand2b_1 _23_ (.Y(output_no[3]),
    .B(_06_),
    .A_N(_01_));
 sg13g2_nor2b_1 _24_ (.A(input_ni[2]),
    .B_N(ena_i),
    .Y(_07_));
 sg13g2_nand2b_1 _25_ (.Y(_08_),
    .B(ena_i),
    .A_N(input_ni[2]));
 sg13g2_nor2_1 _26_ (.A(_00_),
    .B(_08_),
    .Y(output_o[4]));
 sg13g2_nand2b_1 _27_ (.Y(output_no[4]),
    .B(_07_),
    .A_N(_00_));
 sg13g2_nor2_1 _28_ (.A(_03_),
    .B(_08_),
    .Y(output_o[5]));
 sg13g2_nand2_1 _29_ (.Y(output_no[5]),
    .A(_02_),
    .B(_07_));
 sg13g2_nor2_1 _30_ (.A(_05_),
    .B(_08_),
    .Y(output_o[6]));
 sg13g2_nand2_1 _31_ (.Y(output_no[6]),
    .A(_04_),
    .B(_07_));
 sg13g2_and2_1 _32_ (.A(_06_),
    .B(_07_),
    .X(output_o[7]));
 sg13g2_nand2_1 _33_ (.Y(output_no[7]),
    .A(_06_),
    .B(_07_));
 sg13g2_decap_8 FILLER_0_0 ();
 sg13g2_decap_8 FILLER_0_7 ();
 sg13g2_decap_8 FILLER_0_14 ();
 sg13g2_decap_8 FILLER_0_21 ();
 sg13g2_decap_8 FILLER_0_28 ();
 sg13g2_decap_8 FILLER_0_35 ();
 sg13g2_decap_8 FILLER_0_42 ();
 sg13g2_decap_4 FILLER_0_49 ();
 sg13g2_fill_2 FILLER_0_62 ();
 sg13g2_decap_8 FILLER_0_77 ();
 sg13g2_fill_1 FILLER_0_84 ();
 sg13g2_decap_8 FILLER_0_97 ();
 sg13g2_decap_8 FILLER_0_104 ();
 sg13g2_decap_8 FILLER_0_111 ();
 sg13g2_decap_8 FILLER_0_118 ();
 sg13g2_decap_8 FILLER_0_125 ();
 sg13g2_decap_8 FILLER_0_132 ();
 sg13g2_decap_8 FILLER_0_139 ();
 sg13g2_decap_8 FILLER_0_146 ();
 sg13g2_fill_1 FILLER_0_153 ();
 sg13g2_decap_8 FILLER_1_0 ();
 sg13g2_decap_8 FILLER_1_7 ();
 sg13g2_decap_8 FILLER_1_14 ();
 sg13g2_decap_8 FILLER_1_21 ();
 sg13g2_decap_8 FILLER_1_28 ();
 sg13g2_decap_8 FILLER_1_35 ();
 sg13g2_decap_8 FILLER_1_42 ();
 sg13g2_decap_8 FILLER_1_49 ();
 sg13g2_decap_8 FILLER_1_61 ();
 sg13g2_fill_2 FILLER_1_68 ();
 sg13g2_decap_8 FILLER_1_93 ();
 sg13g2_decap_8 FILLER_1_100 ();
 sg13g2_decap_8 FILLER_1_107 ();
 sg13g2_decap_8 FILLER_1_114 ();
 sg13g2_decap_8 FILLER_1_121 ();
 sg13g2_decap_8 FILLER_1_128 ();
 sg13g2_decap_8 FILLER_1_135 ();
 sg13g2_decap_8 FILLER_1_142 ();
 sg13g2_decap_4 FILLER_1_149 ();
 sg13g2_fill_1 FILLER_1_153 ();
 sg13g2_decap_8 FILLER_2_0 ();
 sg13g2_decap_8 FILLER_2_7 ();
 sg13g2_decap_8 FILLER_2_14 ();
 sg13g2_decap_8 FILLER_2_21 ();
 sg13g2_decap_8 FILLER_2_28 ();
 sg13g2_decap_8 FILLER_2_35 ();
 sg13g2_decap_8 FILLER_2_42 ();
 sg13g2_decap_8 FILLER_2_49 ();
 sg13g2_decap_8 FILLER_2_56 ();
 sg13g2_decap_8 FILLER_2_63 ();
 sg13g2_decap_8 FILLER_2_70 ();
 sg13g2_decap_8 FILLER_2_77 ();
 sg13g2_decap_8 FILLER_2_84 ();
 sg13g2_decap_8 FILLER_2_91 ();
 sg13g2_decap_8 FILLER_2_98 ();
 sg13g2_decap_8 FILLER_2_105 ();
 sg13g2_decap_8 FILLER_2_112 ();
 sg13g2_decap_8 FILLER_2_119 ();
 sg13g2_decap_8 FILLER_2_126 ();
 sg13g2_decap_8 FILLER_2_133 ();
 sg13g2_decap_8 FILLER_2_140 ();
 sg13g2_decap_8 FILLER_2_147 ();
 sg13g2_decap_8 FILLER_3_0 ();
 sg13g2_decap_8 FILLER_3_7 ();
 sg13g2_decap_8 FILLER_3_14 ();
 sg13g2_decap_8 FILLER_3_21 ();
 sg13g2_decap_8 FILLER_3_28 ();
 sg13g2_decap_8 FILLER_3_35 ();
 sg13g2_decap_8 FILLER_3_42 ();
 sg13g2_decap_8 FILLER_3_49 ();
 sg13g2_decap_8 FILLER_3_56 ();
 sg13g2_decap_8 FILLER_3_63 ();
 sg13g2_decap_8 FILLER_3_70 ();
 sg13g2_decap_8 FILLER_3_77 ();
 sg13g2_decap_8 FILLER_3_84 ();
 sg13g2_decap_8 FILLER_3_91 ();
 sg13g2_decap_8 FILLER_3_98 ();
 sg13g2_decap_8 FILLER_3_105 ();
 sg13g2_decap_8 FILLER_3_112 ();
 sg13g2_decap_8 FILLER_3_119 ();
 sg13g2_decap_8 FILLER_3_126 ();
 sg13g2_decap_8 FILLER_3_133 ();
 sg13g2_decap_8 FILLER_3_140 ();
 sg13g2_decap_8 FILLER_3_147 ();
 sg13g2_decap_8 FILLER_4_0 ();
 sg13g2_decap_8 FILLER_4_7 ();
 sg13g2_decap_8 FILLER_4_14 ();
 sg13g2_decap_8 FILLER_4_21 ();
 sg13g2_decap_8 FILLER_4_28 ();
 sg13g2_decap_8 FILLER_4_35 ();
 sg13g2_decap_8 FILLER_4_42 ();
 sg13g2_decap_8 FILLER_4_49 ();
 sg13g2_decap_8 FILLER_4_56 ();
 sg13g2_decap_8 FILLER_4_63 ();
 sg13g2_decap_8 FILLER_4_70 ();
 sg13g2_decap_8 FILLER_4_77 ();
 sg13g2_decap_8 FILLER_4_84 ();
 sg13g2_decap_8 FILLER_4_91 ();
 sg13g2_decap_8 FILLER_4_98 ();
 sg13g2_decap_8 FILLER_4_105 ();
 sg13g2_decap_8 FILLER_4_112 ();
 sg13g2_decap_8 FILLER_4_119 ();
 sg13g2_decap_8 FILLER_4_126 ();
 sg13g2_decap_8 FILLER_4_133 ();
 sg13g2_decap_8 FILLER_4_140 ();
 sg13g2_decap_8 FILLER_4_147 ();
 sg13g2_decap_8 FILLER_5_0 ();
 sg13g2_decap_8 FILLER_5_7 ();
 sg13g2_decap_8 FILLER_5_14 ();
 sg13g2_decap_8 FILLER_5_21 ();
 sg13g2_decap_8 FILLER_5_28 ();
 sg13g2_decap_8 FILLER_5_35 ();
 sg13g2_decap_8 FILLER_5_42 ();
 sg13g2_decap_8 FILLER_5_49 ();
 sg13g2_decap_8 FILLER_5_56 ();
 sg13g2_decap_8 FILLER_5_63 ();
 sg13g2_decap_8 FILLER_5_70 ();
 sg13g2_decap_8 FILLER_5_77 ();
 sg13g2_decap_8 FILLER_5_84 ();
 sg13g2_decap_8 FILLER_5_91 ();
 sg13g2_decap_8 FILLER_5_98 ();
 sg13g2_decap_8 FILLER_5_105 ();
 sg13g2_decap_8 FILLER_5_112 ();
 sg13g2_decap_8 FILLER_5_119 ();
 sg13g2_decap_8 FILLER_5_126 ();
 sg13g2_decap_8 FILLER_5_133 ();
 sg13g2_decap_8 FILLER_5_140 ();
 sg13g2_decap_8 FILLER_5_147 ();
 sg13g2_decap_8 FILLER_6_0 ();
 sg13g2_decap_8 FILLER_6_7 ();
 sg13g2_decap_8 FILLER_6_14 ();
 sg13g2_decap_8 FILLER_6_21 ();
 sg13g2_decap_8 FILLER_6_28 ();
 sg13g2_decap_8 FILLER_6_35 ();
 sg13g2_decap_8 FILLER_6_42 ();
 sg13g2_decap_8 FILLER_6_49 ();
 sg13g2_decap_4 FILLER_6_56 ();
 sg13g2_fill_2 FILLER_6_60 ();
 sg13g2_decap_4 FILLER_6_66 ();
 sg13g2_fill_2 FILLER_6_74 ();
 sg13g2_fill_1 FILLER_6_76 ();
 sg13g2_decap_8 FILLER_6_87 ();
 sg13g2_decap_8 FILLER_6_94 ();
 sg13g2_decap_8 FILLER_6_101 ();
 sg13g2_decap_8 FILLER_6_108 ();
 sg13g2_decap_8 FILLER_6_115 ();
 sg13g2_decap_8 FILLER_6_122 ();
 sg13g2_decap_8 FILLER_6_129 ();
 sg13g2_decap_8 FILLER_6_136 ();
 sg13g2_decap_8 FILLER_6_143 ();
 sg13g2_decap_4 FILLER_6_150 ();
 sg13g2_decap_8 FILLER_7_0 ();
 sg13g2_decap_8 FILLER_7_7 ();
 sg13g2_decap_8 FILLER_7_14 ();
 sg13g2_decap_8 FILLER_7_21 ();
 sg13g2_decap_8 FILLER_7_28 ();
 sg13g2_decap_8 FILLER_7_35 ();
 sg13g2_decap_8 FILLER_7_42 ();
 sg13g2_decap_4 FILLER_7_49 ();
 sg13g2_fill_2 FILLER_7_53 ();
 sg13g2_decap_8 FILLER_7_70 ();
 sg13g2_fill_1 FILLER_7_85 ();
 sg13g2_decap_8 FILLER_7_96 ();
 sg13g2_decap_8 FILLER_7_103 ();
 sg13g2_decap_8 FILLER_7_110 ();
 sg13g2_decap_8 FILLER_7_117 ();
 sg13g2_decap_8 FILLER_7_124 ();
 sg13g2_decap_8 FILLER_7_131 ();
 sg13g2_decap_8 FILLER_7_138 ();
 sg13g2_decap_8 FILLER_7_145 ();
 sg13g2_fill_2 FILLER_7_152 ();
endmodule
