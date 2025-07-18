v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N -230 100 -230 120 {
lab=GND}
N 390 100 390 130 {
lab=GND}
N -140 100 -140 120 {
lab=GND}
N -230 0 -230 40 {
lab=Vdd}
N -140 30 -140 40 {
lab=en_p}
N -80 100 -80 120 {
lab=GND}
N -80 30 -80 40 {
lab=en_n}
N 200 50 240 50 {
lab=en_n}
N 200 70 240 70 {
lab=en_p}
N 540 20 640 20 {
lab=Vout}
N 640 20 640 40 {
lab=Vout}
N -20 20 240 20 {
lab=#net1}
N -20 20 -20 40 {
lab=#net1}
N 640 100 640 130 {
lab=GND}
N 390 -110 390 -90 {
lab=Vdd}
N 390 -30 390 -20 {
lab=#net2}
N -20 100 -20 120 {
lab=GND}
N 640 -10 640 20 {
lab=Vout}
C {devices/code_shown.sym} 270 -530 0 0 {name=SETUP only_toplevel=true
format="tcleval( @value )"
value="

.lib CACE\{PDK_ROOT\}/CACE\{PDK\}/libs.tech/ngspice/models/cornerMOSlv.lib mos_CACE\{corner\}
.lib cornerRES.lib res_typ

.include CACE\{DUT_path\}

.temp CACE\{temperature\}
"}
C {devices/code_shown.sym} -230 -520 0 0 {name=NGSPICE only_toplevel=true 
value="
.options noacct
.control
save all 
ac dec 101 1Meg 10G 
meas ac vout_at FIND vout AT=100MEG
let PSRR=20*log10(-vout_at)
print PSRR

echo $&PSRR > CACE\{simpath\}/CACE\{filename\}_CACE\{N\}.data

.endc
"}
C {devices/vsource.sym} -230 70 0 0 {name=Vpow value="dc 1.2 ac 1"}
C {devices/title.sym} -130 260 0 0 {name=l5 author="Copyright 2023 IHP PDK Authors"}
C {devices/gnd.sym} 390 130 0 0 {name=l2 lab=GND}
C {devices/ammeter.sym} 390 -60 0 0 {name=Vp}
C {devices/gnd.sym} -230 120 0 0 {name=l1 lab=GND}
C {devices/vsource.sym} -140 70 0 0 {name=Ven value=1.2
}
C {devices/gnd.sym} -140 120 0 0 {name=l3 lab=GND}
C {devices/lab_pin.sym} -140 30 1 0 {name=p2 sig_type=std_logic lab=en_p}
C {devices/lab_pin.sym} -230 0 1 0 {name=p4 sig_type=std_logic lab=Vdd}
C {devices/vsource.sym} -80 70 0 0 {name=Ven1 value=0}
C {devices/gnd.sym} -80 120 0 0 {name=l7 lab=GND}
C {devices/lab_pin.sym} -80 30 1 0 {name=p5 sig_type=std_logic lab=en_n}
C {devices/lab_pin.sym} 390 -110 1 0 {name=p6 sig_type=std_logic lab=Vdd}
C {devices/lab_pin.sym} 200 70 0 0 {name=p8 sig_type=std_logic lab=en_p}
C {devices/lab_pin.sym} 200 50 0 0 {name=p9 sig_type=std_logic lab=en_n}
C {devices/gnd.sym} 640 130 0 0 {name=l8 lab=GND}
C {devices/vsource.sym} -20 70 0 0 {name=V1 value=1.2}
C {devices/gnd.sym} -20 120 0 0 {name=l6 lab=GND}
C {devices/res.sym} 640 70 0 0 {name=R1
value=10k
footprint=1206
device=resistor
m=1}
C {devices/lab_pin.sym} 640 -10 1 0 {name=p1 sig_type=std_logic lab=Vout}
C {transmission_gate.sym} 390 40 0 0 {name=x1}
