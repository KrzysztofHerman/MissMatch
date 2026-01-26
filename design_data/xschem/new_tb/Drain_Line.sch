v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 870 -830 870 -740 {lab=Drain}
N 790 -740 870 -740 {lab=Drain}
N 700 -830 700 -740 {lab=Drain}
N 790 -740 790 -670 {lab=Drain}
N 700 -740 790 -740 {lab=Drain}
N 970 -670 1160 -670 {lab=Drain}
N 970 -670 970 -510 {lab=Drain}
N 1070 -830 1070 -740 {lab=Drain}
N 1160 -740 1240 -740 {lab=Drain}
N 1240 -830 1240 -740 {lab=Drain}
N 1160 -740 1160 -670 {lab=Drain}
N 1070 -740 1160 -740 {lab=Drain}
N 700 -970 700 -890 {lab=Dsense}
N 790 -970 870 -970 {lab=Dsense}
N 870 -970 870 -890 {lab=Dsense}
N 1070 -970 1070 -890 {lab=Dforce}
N 1160 -970 1240 -970 {lab=Dforce}
N 1240 -970 1240 -890 {lab=Dforce}
N 790 -1090 1360 -1090 {lab=Dsense}
N 790 -1090 790 -970 {lab=Dsense}
N 700 -970 790 -970 {lab=Dsense}
N 1160 -1060 1360 -1060 {lab=Dforce}
N 1160 -1060 1160 -970 {lab=Dforce}
N 1070 -970 1160 -970 {lab=Dforce}
N 1280 -860 1300 -860 {lab=ctrl_p}
N 1300 -1130 1300 -860 {lab=ctrl_p}
N 890 -1230 890 -1130 {lab=ctrl_p}
N 890 -1130 1300 -1130 {lab=ctrl_p}
N 620 -1130 620 -860 {lab=ctrl_p}
N 620 -860 660 -860 {lab=ctrl_p}
N 1070 -860 1120 -860 {lab=#net1}
N 830 -860 870 -860 {lab=#net1}
N 700 -860 740 -860 {lab=#net2}
N 1350 -1000 1360 -1000 {lab=Vss}
N 1190 -860 1240 -860 {lab=#net2}
N 970 -950 970 -930 {lab=#net1}
N 970 -930 1120 -930 {lab=#net1}
N 830 -930 830 -860 {lab=#net1}
N 1120 -930 1120 -860 {lab=#net1}
N 970 -1030 970 -1010 {lab=1.2V}
N 740 -860 740 -810 {lab=#net2}
N 740 -810 970 -810 {lab=#net2}
N 970 -810 970 -780 {lab=#net2}
N 970 -720 970 -700 {lab=Vss}
N 970 -700 1350 -700 {lab=Vss}
N 1350 -1000 1350 -700 {lab=Vss}
N 790 -670 970 -670 {lab=Drain}
N 970 -810 1190 -810 {lab=#net2}
N 1190 -860 1190 -810 {lab=#net2}
N 620 -1130 890 -1130 {lab=ctrl_p}
N 930 -860 1030 -860 {lab=ctrl_n}
N 830 -930 970 -930 {lab=#net1}
N 970 -1030 1360 -1030 {lab=1.2V}
N 930 -1230 930 -860 {lab=ctrl_n}
N 910 -860 930 -860 {lab=ctrl_n}
C {devices/iopin.sym} 1360 -1000 0 0 {name=p4 lab=Vss}
C {devices/ipin.sym} 930 -1230 1 0 {name=p3 lab=ctrl_n}
C {devices/iopin.sym} 1360 -1030 0 0 {name=p8 lab=1.2V}
C {devices/iopin.sym} 1360 -1090 0 0 {name=p13 lab=Dsense}
C {devices/iopin.sym} 970 -510 1 0 {name=p14 lab=Drain}
C {devices/iopin.sym} 1360 -1060 0 0 {name=p15 lab=Dforce}
C {sg13g2_pr/sg13_lv_nmos.sym} 680 -860 0 0 {name=M4
l=\{m1_l\}
w=\{m1_w\}
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 890 -860 0 1 {name=M8
l=\{m2_l\}
w=\{m2_w\}
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 1050 -860 0 0 {name=M9
l=\{m2_l\}
w=\{m2_w\}
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 1260 -860 0 1 {name=M10
l=\{m1_l\}
w=\{m1_w\}
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {title-3.sym} 200 150 0 0 {name=l2 author="IHP Open PDK Authors 2025" title="Drain line control circuit" rev=1.0 lock=true}
C {devices/ipin.sym} 890 -1230 1 0 {name=p1 lab=ctrl_p}
C {sg13g2_pr/ptap1.sym} 970 -750 2 0 {name=R1
model=ptap1
spiceprefix=X
w=10.0e-6
l=1.0e-6
}
C {sg13g2_pr/ntap1.sym} 970 -980 2 0 {name=R2
model=ntap1
spiceprefix=X
w=10.0e-6
l=1.0e-6
}
