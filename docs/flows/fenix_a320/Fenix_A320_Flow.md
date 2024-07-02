# Fenix A320 Flow

## Preliminary Cockpit Preperation

### Safety and Security

| Check                  | Status      |
|------------------------|-------------|
| Engine Master Switches | OFF         |
| Engine Mode Selector   | Norm        |
| Radar Sys Switch       | OFF         |
| PWS Switch             | OFF         |
| Gain Knob              | Cal         |
| Multiscan Switch       | Auto        |
| GCS Switch             | Auto        |
| Landing Gear Lever     | Up Position |
| Wiper Selectors        | OFF         |

### Power Up

| Check                             | Status       |
|-----------------------------------|--------------|
| Battery Voltage                   | > 25.5V      |
| Battery 1/2                       | ON           |
| EXT Power                         | ON           |
| Wait for Boot Up                  | 3 Beeps      |
| If Weather Condition too hot/cold | Start APU    |
| Radio VHF 1/2/INT/CAB             | Listen ON    |
| APU Fire Test                     | CHECK        |
| APU Master Switch                 | ON           |
| After 3s APU Start                | ON           |
| When APU is Available             | Start Chrono |
| After 3min APU Bleed              | ON           |
| IRS 1/2/3                         | NAV          |
| Cockpit Lights                    | Adjust       |

### FMS Preinitilization

Note: Select the secondary nav data base on the A/C status
page to delete the whole flight plan.

| Check           | Status        |
|-----------------|---------------|
| AOC -> FLT INIT | INIT DATA REQ |
| A/C Status      | CHECK         |
| INIT PAGE       | INIT REQUEST  |
| INIT PAGE       | FLT NBR       |

### Aircraft Status

Note: If engine page is xxx then activate FADEC GND POWER at the upper overhead panel. 0.5 oil per hour.

| Check                  | Status                  |
|------------------------|-------------------------|
| RECALL                 | PRESS 3s                |
| Aircraft Configuration | Check EFB               |
| Door Oxygen Page       | > 1000psi               |
| Hydraulic Page         | Arrow in the box        |
| Engine Page            | Check Oil above minimum |
| Flap lever indication  | Matching                |
| Speedbrake             | Retracted & Disarmed    |
| Parking Brake          | Check Pressure          |
| Brake Check (Release Parking Brake)                | Check                |

### Preliminary Performance Calculation

Note: 200kg fuel = 5min flying. Normal Op: 1+F Take Off

| Check                | Status            |
|----------------------|-------------------|
| Fuel Calc            | Ckeck/Adjust      |
| EFB Mass/Weight      | Adjust/Load       |
| Take Off Performance | Adjust/Calc/Check |
| TOPL / Stop Margin   | Ckeck             |
| Fuel Calc            | Ckeck/Adjust      |

## Preflight Procedure
<img width="700" alt="image" src="https://github.com/Zwelckovich/flightsim/blob/main/docs/flows/fenix_a320/pics/a320flow.png">

