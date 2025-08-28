                    MISMATCH ARRAY 4x4 - NAMING CONVENTION
    ═══════════════════════════════════════════════════════════════════════
    
                         D_COL0    D_COL1    D_COL2    D_COL3
                           ↑         ↑         ↑         ↑
                           │         │         │         │
                           │         │         │         │
      G_ROW0 ←─────────[T00]─────[T01]─────[T02]─────[T03]─────────→ G_ROW0
      S_R0   ←─────────────────────────────────────────────────────→ S_R0
                           │         │         │         │
                           │         │         │         │
      G_ROW1 ←─────────[T10]─────[T11]─────[T12]─────[T13]─────────→ G_ROW1
      S_R1   ←─────────────────────────────────────────────────────→ S_R1
                           │         │         │         │
                           │         │         │         │
      G_ROW2 ←─────────[T20]─────[T21]─────[T22]─────[T23]─────────→ G_ROW2
      S_R2   ←─────────────────────────────────────────────────────→ S_R2
                           │         │         │         │
                           │         │         │         │
      G_ROW3 ←─────────[T30]─────[T31]─────[T32]─────[T33]─────────→ G_ROW3
      S_R3   ←─────────────────────────────────────────────────────→ S_R3
                           │         │         │         │
                           │         │         │         │
                           ↓         ↓         ↓         ↓
                         D_COL0    D_COL1    D_COL2    D_COL3

    ═══════════════════════════════════════════════════════════════════════
    
    LEGEND:
    -------
    • G_ROWx  : Gate connections (M3)      - HORIZONTAL buses (exit LEFT/RIGHT)
    • D_COLx  : Drain connections (TM1)    - VERTICAL buses (exit TOP/BOTTOM)  
    • S_Rx    : Source connections (TM2)    - HORIZONTAL buses (exit LEFT/RIGHT)
    • [Txy]   : Transistor at row x, column y
    
    METAL LAYERS:
    -------------
    • Gates   : Poly → Contact → M1 → Via1 → M2 → Via2 → M3
    • Drains  : M1 → Via1 → M2 → Via2 → M3 → Via3 → M4 → Via4 → M5 → TopVia1 → TopMetal1
    • Sources : M1 → Via1 → M2 → Via2 → M3 → Via3 → M4 → Via4 → M5 → TopVia1 → TopMetal1 → TopVia2 → TopMetal2
    
    NOTES:
    ------
    • Row 0 = TOP of array (visual orientation)
    • Row 3 = BOTTOM of array (visual orientation)
    • All buses extend to guard ring edges + 1.5μm
    • Poly extension for gates: 1.5μm above transistor
    • M1 extension for drain/source: 1.0μm outside transistor