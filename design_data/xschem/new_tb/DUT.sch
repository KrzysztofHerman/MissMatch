v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
C {devices/iopin.sym} 0 0 2 0  {name=p9 lab=B}
C {devices/iopin.sym} 100 0 1 1  {name=p61 lab=D1}
P 4 5 0 0 200 0 200 200 0 200 0 0 {}
N 170 70 170 110 {lab=B}
N 170 170 170 190 {lab=B}
N 90 100 90 140 {lab=S1}
N 10 70 50 70 {lab=G1}
N 90 20 90 40 {lab=D1}
N 10 20 90 20 {lab=D1}
N 10 190 170 190 {lab=B}
N 10 140 90 140 {lab=S1}
N 10 10 10 20 {lab=D1}
N 10 60 10 70 {lab=G1}
N 10 130 10 140 {lab=S1}
N 10 180 10 190 {lab=B}
N 170 60 170 70 {lab=B}
N 90 70 170 70 {lab=B}
C {lab_pin.sym} 10 15 2 0  {name=p11 sig_type=std_logic lab=D1}
C {lab_pin.sym} 10 60 2 0  {name=p21 sig_type=std_logic lab=G1}
C {lab_pin.sym} 10 130 2 0  {name=p31 sig_type=std_logic lab=S1}
C {lab_pin.sym} 10 180 2 0  {name=p41 sig_type=std_logic lab=B}
C {lab_pin.sym} 170 60 1 2  {name=p51 sig_type=std_logic lab=sub!}
C {sg13g2_pr/ptap1.sym} 170 140 2 0 {name=R1 
model=ptap1
spiceprefix=X
 w=7.8e-07
l=7.8e-07}
C {sg13g2_pr/sg13_lv_nmos.sym} 70 70 0 0 {name=M1 
model=sg13_lv_nmos
spiceprefix=X
 w=1.15u
l=0.15u
ng=1
m=1}
P 4 5 0 200 200 200 200 400 0 400 0 200 {}
N 170 270 170 310 {lab=B}
N 170 370 170 390 {lab=B}
N 90 300 90 340 {lab=S2}
N 10 270 50 270 {lab=G2}
N 90 220 90 240 {lab=D1}
N 10 220 90 220 {lab=D1}
N 10 390 170 390 {lab=B}
N 10 340 90 340 {lab=S2}
N 10 210 10 220 {lab=D1}
N 10 260 10 270 {lab=G2}
N 10 330 10 340 {lab=S2}
N 10 380 10 390 {lab=B}
N 170 260 170 270 {lab=B}
N 90 270 170 270 {lab=B}
C {lab_pin.sym} 10 215 2 0  {name=p12 sig_type=std_logic lab=D1}
C {lab_pin.sym} 10 260 2 0  {name=p22 sig_type=std_logic lab=G2}
C {lab_pin.sym} 10 330 2 0  {name=p32 sig_type=std_logic lab=S2}
C {lab_pin.sym} 10 380 2 0  {name=p42 sig_type=std_logic lab=B}
C {lab_pin.sym} 170 260 1 2  {name=p52 sig_type=std_logic lab=sub!}
C {sg13g2_pr/ptap1.sym} 170 340 2 0 {name=R2 
model=ptap1
spiceprefix=X
 w=7.8e-07
l=7.8e-07}
C {sg13g2_pr/sg13_lv_nmos.sym} 70 270 0 0 {name=M2 
model=sg13_lv_nmos
spiceprefix=X
 w=1.15u
l=0.15u
ng=1
m=1}
C {devices/iopin.sym} 300 0 1 1  {name=p62 lab=D2}
P 4 5 200 0 400 0 400 200 200 200 200 0 {}
N 370 70 370 110 {lab=B}
N 370 170 370 190 {lab=B}
N 290 100 290 140 {lab=S1}
N 210 70 250 70 {lab=G1}
N 290 20 290 40 {lab=D2}
N 210 20 290 20 {lab=D2}
N 210 190 370 190 {lab=B}
N 210 140 290 140 {lab=S1}
N 210 10 210 20 {lab=D2}
N 210 60 210 70 {lab=G1}
N 210 130 210 140 {lab=S1}
N 210 180 210 190 {lab=B}
N 370 60 370 70 {lab=B}
N 290 70 370 70 {lab=B}
C {lab_pin.sym} 210 15 2 0  {name=p13 sig_type=std_logic lab=D2}
C {lab_pin.sym} 210 60 2 0  {name=p23 sig_type=std_logic lab=G1}
C {lab_pin.sym} 210 130 2 0  {name=p33 sig_type=std_logic lab=S1}
C {lab_pin.sym} 210 180 2 0  {name=p43 sig_type=std_logic lab=B}
C {lab_pin.sym} 370 60 1 2  {name=p53 sig_type=std_logic lab=sub!}
C {sg13g2_pr/ptap1.sym} 370 140 2 0 {name=R3 
model=ptap1
spiceprefix=X
 w=7.8e-07
l=7.8e-07}
C {sg13g2_pr/sg13_lv_nmos.sym} 270 70 0 0 {name=M3 
model=sg13_lv_nmos
spiceprefix=X
 w=1.15u
l=0.15u
ng=1
m=1}
P 4 5 200 200 400 200 400 400 200 400 200 200 {}
N 370 270 370 310 {lab=B}
N 370 370 370 390 {lab=B}
N 290 300 290 340 {lab=S2}
N 210 270 250 270 {lab=G2}
N 290 220 290 240 {lab=D2}
N 210 220 290 220 {lab=D2}
N 210 390 370 390 {lab=B}
N 210 340 290 340 {lab=S2}
N 210 210 210 220 {lab=D2}
N 210 260 210 270 {lab=G2}
N 210 330 210 340 {lab=S2}
N 210 380 210 390 {lab=B}
N 370 260 370 270 {lab=B}
N 290 270 370 270 {lab=B}
C {lab_pin.sym} 210 215 2 0  {name=p14 sig_type=std_logic lab=D2}
C {lab_pin.sym} 210 260 2 0  {name=p24 sig_type=std_logic lab=G2}
C {lab_pin.sym} 210 330 2 0  {name=p34 sig_type=std_logic lab=S2}
C {lab_pin.sym} 210 380 2 0  {name=p44 sig_type=std_logic lab=B}
C {lab_pin.sym} 370 260 1 2  {name=p54 sig_type=std_logic lab=sub!}
C {sg13g2_pr/ptap1.sym} 370 340 2 0 {name=R4 
model=ptap1
spiceprefix=X
 w=7.8e-07
l=7.8e-07}
C {sg13g2_pr/sg13_lv_nmos.sym} 270 270 0 0 {name=M4 
model=sg13_lv_nmos
spiceprefix=X
 w=1.15u
l=0.15u
ng=1
m=1}
C {devices/iopin.sym} 0 70 2 0  {name=p71 lab=G1}
C {devices/iopin.sym} 0 140 2 0  {name=p81 lab=S1}
C {devices/iopin.sym} 0 270 2 0  {name=p72 lab=G2}
C {devices/iopin.sym} 0 340 2 0  {name=p82 lab=S2}
