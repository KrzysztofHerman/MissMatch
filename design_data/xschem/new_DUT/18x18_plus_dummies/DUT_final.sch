v {xschem version=3.4.6 file_version=1.2}
G {}
K {type=schematic}
V {}
S {}
E {}
N 200 400 400 400 {lab=D[0:4]}
N 200 440 400 440 {lab=G[0:4]}
N 200 500 400 500 {lab=S[0:4]}
N 200 560 400 560 {lab=B}
N 720 980 3200 980 {lab=G[0]}
N 720 1040 3200 1040 {lab=S[0]}
N 730 1460 3210 1460 {lab=G[1]}
N 720 1520 3200 1520 {lab=S[1]}
N 720 1940 3200 1940 {lab=G[2]}
N 720 2000 3200 2000 {lab=S[2]}
N 720 2420 3200 2420 {lab=G[3]}
N 720 2480 3200 2480 {lab=S[3]}
N 720 2900 3200 2900 {lab=G[4]}
N 720 2960 3200 2960 {lab=S[4]}
N 1050 680 1050 2720 {lab=D[0]}
N 1650 680 1650 2720 {lab=D[1]}
N 2850 680 2850 2720 {lab=D[3]}
N 3450 680 3450 2720 {lab=D[4]}
N 880 800 960 800 {lab=B}
N 1480 800 1560 800 {lab=B}
N 2080 800 2160 800 {lab=B}
N 2680 800 2760 800 {lab=B}
N 3280 800 3360 800 {lab=B}
N 880 1280 960 1280 {lab=B}
N 1480 1280 1560 1280 {lab=B}
N 2080 1280 2160 1280 {lab=B}
N 2680 1280 2760 1280 {lab=B}
N 3280 1280 3360 1280 {lab=B}
N 880 1760 960 1760 {lab=B}
N 1480 1760 1560 1760 {lab=B}
N 2080 1760 2160 1760 {lab=B}
N 2680 1760 2760 1760 {lab=B}
N 3280 1760 3360 1760 {lab=B}
N 880 2240 960 2240 {lab=B}
N 1480 2240 1560 2240 {lab=B}
N 2080 2240 2160 2240 {lab=B}
N 2680 2240 2760 2240 {lab=B}
N 3280 2240 3360 2240 {lab=B}
N 880 2720 960 2720 {lab=B}
N 1480 2720 1560 2720 {lab=B}
N 2080 2720 2160 2720 {lab=B}
N 2680 2720 2760 2720 {lab=B}
N 3280 2720 3360 2720 {lab=B}
N 2240 680 2250 680 {lab=D[2]}
N 2250 680 2250 2730 {lab=D[2]}
N 2840 680 2850 680 {lab=D[3]}
N 3440 680 3450 680 {lab=D[4]}
N 1610 680 1650 680 {lab=D[1]}
N 1040 680 1050 680 {lab=D[0]}
C {devices/lab_pin.sym} 200 400 0 0 {name=lab_D[0:4]_200_400 lab=D[0:4] dir=inout}
C {devices/iopin.sym} 400 400 0 0 {name=D_pin lab=D dir=inout}
C {devices/lab_pin.sym} 200 440 0 0 {name=lab_G[0:4]_200_440 lab=G[0:4] dir=inout}
C {devices/iopin.sym} 400 440 0 0 {name=G_pin lab=G dir=inout}
C {devices/lab_pin.sym} 200 500 0 0 {name=lab_S[0:4]_200_500 lab=S[0:4] dir=inout}
C {devices/iopin.sym} 400 500 0 0 {name=S_pin lab=S dir=inout}
C {devices/lab_pin.sym} 200 560 0 0 {name=lab_B_200_560 lab=B dir=inout}
C {devices/iopin.sym} 400 560 0 0 {name=B_pin lab=B dir=inout}
C {W2p4u_L2p08u.sym} 1000 1010 0 0 {name=X00}
C {W2p4u_L1p04u.sym} 1600 1010 0 0 {name=X01}
C {W2p4u_L0p52u.sym} 2200 1010 0 0 {name=X02}
C {W2p4u_L0p26u.sym} 2800 1010 0 0 {name=X03}
C {W2p4u_L0p13u.sym} 3400 1010 0 0 {name=X04}
C {W1p2u_L2p08u.sym} 1000 1490 0 0 {name=X10}
C {W1p2u_L1p04u.sym} 1600 1490 0 0 {name=X11}
C {W1p2u_L0p52u.sym} 2200 1490 0 0 {name=X12}
C {W1p2u_L0p26u.sym} 2800 1490 0 0 {name=X13}
C {W1p2u_L0p13u.sym} 3400 1490 0 0 {name=X14}
C {W0p6u_L2p08u.sym} 1000 1970 0 0 {name=X20}
C {W0p6u_L1p04u.sym} 1600 1970 0 0 {name=X21}
C {W0p6u_L0p52u.sym} 2200 1970 0 0 {name=X22}
C {W0p6u_L0p26u.sym} 2800 1970 0 0 {name=X23}
C {W0p6u_L0p13u.sym} 3400 1970 0 0 {name=X24}
C {W0p3u_L2p08u.sym} 1000 2450 0 0 {name=X30}
C {W0p3u_L1p04u.sym} 1600 2450 0 0 {name=X31}
C {W0p3u_L0p52u.sym} 2200 2450 0 0 {name=X32}
C {W0p3u_L0p26u.sym} 2800 2460 0 0 {name=X33}
C {W0p3u_L0p13u.sym} 3400 2450 0 0 {name=X34}
C {W0p15u_L2p08u.sym} 1000 2930 0 0 {name=X40}
C {W0p15u_L1p04u.sym} 1600 2930 0 0 {name=X41}
C {W0p15u_L0p52u.sym} 2200 2930 0 0 {name=X42}
C {W0p15u_L0p26u.sym} 2800 2930 0 0 {name=X43}
C {W0p15u_L0p13u.sym} 3400 2930 0 0 {name=X44}
C {devices/lab_pin.sym} 720 980 0 0 {name=lab_G[0]_720_920 lab=G[0] dir=inout}
C {devices/lab_pin.sym} 720 1040 0 0 {name=lab_S[0]_720_1040 lab=S[0] dir=inout}
C {devices/lab_pin.sym} 730 1460 0 0 {name=lab_G[1]_720_1400 lab=G[1] dir=inout}
C {devices/lab_pin.sym} 720 1520 0 0 {name=lab_S[1]_720_1520 lab=S[1] dir=inout}
C {devices/lab_pin.sym} 720 1940 0 0 {name=lab_G[2]_720_1880 lab=G[2] dir=inout}
C {devices/lab_pin.sym} 720 2000 0 0 {name=lab_S[2]_720_2000 lab=S[2] dir=inout}
C {devices/lab_pin.sym} 720 2420 0 0 {name=lab_G[3]_720_2360 lab=G[3] dir=inout}
C {devices/lab_pin.sym} 720 2480 0 0 {name=lab_S[3]_720_2480 lab=S[3] dir=inout}
C {devices/lab_pin.sym} 720 2900 0 0 {name=lab_G[4]_720_2840 lab=G[4] dir=inout}
C {devices/lab_pin.sym} 720 2960 0 0 {name=lab_S[4]_720_2960 lab=S[4] dir=inout}
C {devices/lab_pin.sym} 1040 680 0 0 {name=lab_D[0]_1040_680 lab=D[0] dir=inout}
C {devices/lab_pin.sym} 1610 680 0 0 {name=lab_D[1]_1640_680 lab=D[1] dir=inout}
C {devices/lab_pin.sym} 2240 680 0 0 {name=lab_D[2]_2240_680 lab=D[2] dir=inout}
C {devices/lab_pin.sym} 2840 680 0 0 {name=lab_D[3]_2840_680 lab=D[3] dir=inout}
C {devices/lab_pin.sym} 3440 680 0 0 {name=lab_D[4]_3440_680 lab=D[4] dir=inout}
C {devices/lab_pin.sym} 880 800 0 0 {name=lab_B_880_800 lab=B dir=inout}
C {devices/lab_pin.sym} 1480 800 0 0 {name=lab_B_1480_800 lab=B dir=inout}
C {devices/lab_pin.sym} 2080 800 0 0 {name=lab_B_2080_800 lab=B dir=inout}
C {devices/lab_pin.sym} 2680 800 0 0 {name=lab_B_2680_800 lab=B dir=inout}
C {devices/lab_pin.sym} 3280 800 0 0 {name=lab_B_3280_800 lab=B dir=inout}
C {devices/lab_pin.sym} 880 1280 0 0 {name=lab_B_880_1280 lab=B dir=inout}
C {devices/lab_pin.sym} 1480 1280 0 0 {name=lab_B_1480_1280 lab=B dir=inout}
C {devices/lab_pin.sym} 2080 1280 0 0 {name=lab_B_2080_1280 lab=B dir=inout}
C {devices/lab_pin.sym} 2680 1280 0 0 {name=lab_B_2680_1280 lab=B dir=inout}
C {devices/lab_pin.sym} 3280 1280 0 0 {name=lab_B_3280_1280 lab=B dir=inout}
C {devices/lab_pin.sym} 880 1760 0 0 {name=lab_B_880_1760 lab=B dir=inout}
C {devices/lab_pin.sym} 1480 1760 0 0 {name=lab_B_1480_1760 lab=B dir=inout}
C {devices/lab_pin.sym} 2080 1760 0 0 {name=lab_B_2080_1760 lab=B dir=inout}
C {devices/lab_pin.sym} 2680 1760 0 0 {name=lab_B_2680_1760 lab=B dir=inout}
C {devices/lab_pin.sym} 3280 1760 0 0 {name=lab_B_3280_1760 lab=B dir=inout}
C {devices/lab_pin.sym} 880 2240 0 0 {name=lab_B_880_2240 lab=B dir=inout}
C {devices/lab_pin.sym} 1480 2240 0 0 {name=lab_B_1480_2240 lab=B dir=inout}
C {devices/lab_pin.sym} 2080 2240 0 0 {name=lab_B_2080_2240 lab=B dir=inout}
C {devices/lab_pin.sym} 2680 2240 0 0 {name=lab_B_2680_2240 lab=B dir=inout}
C {devices/lab_pin.sym} 3280 2240 0 0 {name=lab_B_3280_2240 lab=B dir=inout}
C {devices/lab_pin.sym} 880 2720 0 0 {name=lab_B_880_2720 lab=B dir=inout}
C {devices/lab_pin.sym} 1480 2720 0 0 {name=lab_B_1480_2720 lab=B dir=inout}
C {devices/lab_pin.sym} 2080 2720 0 0 {name=lab_B_2080_2720 lab=B dir=inout}
C {devices/lab_pin.sym} 2680 2720 0 0 {name=lab_B_2680_2720 lab=B dir=inout}
C {devices/lab_pin.sym} 3280 2720 0 0 {name=lab_B_3280_2720 lab=B dir=inout}
