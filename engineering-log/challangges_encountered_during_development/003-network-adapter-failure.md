# 003 — Windows Network Adapter Failure

## Status

**Environment incident — partially resolved during broader workstation recovery**

## Date

2026

## System Context

* Device: HP EliteBook 840 G3
* OS: Windows 11 Pro
* Wi-Fi adapter: Intel(R) Dual Band Wireless-AC 8260
* Virtualization: VirtualBox / Hyper-V components present
* Development workload: local AI, Python, Git, package management, remote services

---

## 1. Problem

The development workstation developed severe Windows networking failures.

Observed symptoms included:

* Wi-Fi disappearing from Windows.
* Mobile Hotspot failing immediately.
* Windows reporting inability to configure Mobile Hotspot.
* Network adapters displaying warning states.
* USB tethering becoming affected.
* Network interfaces disappearing from normal network configuration views.
* Device Manager reporting Code 56.
* Loss of reliable internet access during active development.

This became particularly serious because the development workflow depended on internet access for package installation, Git operations, model/runtime downloads, documentation, and client work.

---

## 2. Relevant Hardware

The laptop contained:

```text
Intel(R) Dual Band Wireless-AC 8260
```

The wireless driver information previously showed:

```text
Driver version: 20.70.21.2
Driver date: 10/01/2021
```

The adapter reported that hosted networking was not supported.

---

## 3. Symptoms and Error States

One important Windows error was:

```text
Windows is still setting up the class configuration for this device.
(Code 56)
```

The problem was observed across networking components including:

```text
Intel(R) Dual Band Wireless-AC 8260
Intel(R) Ethernet Connection I219-LM
Generic Mobile Broadband Adapter
Remote NDIS based Internet Sharing Device
```

Some adapters were reported as:

```text
CM_PROB_NEED_CLASS_CONFIG
```

with problem code:

```text
0x38
```

---

## 4. Initial State

At one point, Wi-Fi was functional:

```text
SSID: KONNECT
Band: 2.4 GHz
Channel: 1
Radio type: 802.11n
Signal: approximately 96%
```

The machine could therefore successfully communicate with the wireless network before the later configuration failures.

---

## 5. Mobile Hotspot Failure

The intended workflow was:

```text
KONNECT Wi-Fi
       ↓
Windows laptop
       ↓
Windows Mobile Hotspot
       ↓
Phones / other devices
```

Instead, Mobile Hotspot would immediately disconnect or fail to start.

Windows displayed an error equivalent to:

```text
We can't setup mobile hotspot.
```

This initially suggested a hotspot-specific problem, but subsequent evidence showed that the underlying Windows network stack was also affected.

---

## 6. Major Diagnostic Actions

Various Windows networking diagnostics were performed, including:

```powershell
netsh wlan show drivers
netsh wlan show interfaces
netsh interface show interface
Get-NetAdapter
pnputil /enum-devices /class Net
sc query NetSetupSvc
```

Network services and adapter states were also investigated.

The system contained virtual networking components such as:

```text
VMware Network Adapter VMnet1
VMware Network Adapter VMnet8
Hyper-V Virtual Ethernet Adapter
```

while physical interfaces became unavailable or entered problematic states.

---

## 7. `netcfg -d` Incident

A full network configuration reset had previously been performed using:

```powershell
netcfg -d
```

This command was later recognized as a significant intervention because it removes and rebuilds network configuration components.

Afterward, additional adapter/class configuration problems appeared.

### Engineering lesson

System-wide reset commands are not inherently bad, but they are **high-impact interventions**.

Before using them:

1. Establish the exact failure.
2. Record current configuration.
3. Understand what the command modifies.
4. Prefer the least destructive intervention that can discriminate between hypotheses.

---

## 8. Windows System File Repair

Windows System File Checker was run:

```powershell
sfc /scannow
```

It reported:

```text
Windows Resource Protection found corrupt files
and successfully repaired them.
```

This provided evidence that the Windows installation itself had experienced system-file corruption.

---

## 9. Root-Cause Model

The incident could not safely be reduced to a single component failure.

The evidence pointed toward interaction among:

```text
Windows networking stack
        +
network adapter drivers
        +
network class configuration
        +
virtual networking adapters
        +
Windows system-file state
        +
previous network configuration resets
```

The most reliable conclusion was therefore:

> The workstation's Windows networking configuration and/or driver class configuration had become inconsistent, producing failures across multiple networking interfaces.

---

## 10. Why This Was Important to the AI Project

A local-first AI application is still dependent on its host environment.

The dependency chain is:

```text
AI application
      ↓
Python environment
      ↓
Operating system
      ↓
Network stack
      ↓
Internet / LAN
```

Even when the AI system itself is designed to operate locally, development infrastructure may still require networking for:

* dependency installation,
* GitHub synchronization,
* model downloads,
* package updates,
* documentation,
* client communication,
* remote deployment.

---

## 11. Engineering Lessons

### Lesson 1 — Don't confuse symptoms with layers

"Hotspot doesn't work" does not necessarily mean "hotspot is broken."

The correct investigation expanded downward:

```text
Hotspot
 ↓
Windows networking
 ↓
Network adapters
 ↓
Driver state
 ↓
Network class configuration
 ↓
OS integrity
```

### Lesson 2 — Preserve diagnostic evidence

Before destructive remediation, capture:

```powershell
Get-NetAdapter
netsh wlan show drivers
netsh wlan show interfaces
pnputil /enum-devices /class Net
```

### Lesson 3 — Avoid unnecessary system-wide resets

Prefer:

```text
targeted repair
```

over:

```text
full reset
```

unless evidence justifies the broader intervention.

### Lesson 4 — Development environments are socio-technical systems

The project depends not only on source code but also on:

```text
hardware
OS
drivers
network
runtime
package manager
dependencies
editor
source control
```

---

## 12. Diagnostic Method

```text
Observe
  ↓
Identify affected interfaces
  ↓
Inspect adapter state
  ↓
Inspect driver state
  ↓
Inspect network class configuration
  ↓
Inspect Windows system integrity
  ↓
Separate physical, driver, OS, and configuration hypotheses
  ↓
Apply least-destructive repair
  ↓
Verify each layer independently
```

## 13. Preventive Practice

Maintain a lightweight workstation recovery record containing:

* driver versions,
* Windows version/build,
* network adapter inventory,
* virtualization adapters,
* important development tools,
* backup connectivity options.

For destructive commands, record:

```text
Command
Purpose
Expected effect
Risk
Rollback strategy
Observed result
```
