# 002 — Python Environment Reconstruction

## Status

**Resolved**

## Date

2026-09-06

## System Context

* Project: `LocalAIAgentWithRAG`
* OS: Windows 11 Pro
* Python target: 3.13.15
* Environment: `.venv`
* Package manager: `pip`

---

## 1. Problem

The project had accumulated uncertainty around which Python interpreter was being used and where dependencies were being installed.

Some packages had previously been installed into the global Python environment instead of being isolated within the project's virtual environment.

This created a reproducibility and dependency-isolation problem.

---

## 2. Why This Matters

The intended architecture was:

```text
Project
   ↓
.venv
   ↓
Project-specific Python interpreter
   ↓
Project-specific dependencies
```

Instead, the environment had previously been susceptible to:

```text
Project
   ↓
Global Python
   ↓
Globally installed packages
```

This can create:

* hidden dependencies,
* version conflicts,
* "works on my machine" behavior,
* difficult environment reconstruction,
* accidental system-wide package changes.

---

## 3. Reconstruction Strategy

The environment was rebuilt around Python 3.13.15.

The active interpreter was verified with:

```powershell
python --version
```

Result:

```text
Python 3.13.15
```

The exact interpreter location was verified with:

```powershell
python -c "import sys; print(sys.executable)"
```

Result:

```text
C:\Emmanuel_Heroe\AI-ML-DS\LocalAIAgentWithRAG\.venv\Scripts\python.exe
```

This established that the active interpreter belonged to the project virtual environment.

---

## 4. Pip Verification

Pip was checked using:

```powershell
python -m pip --version
```

The result showed pip operating from the project's `.venv`:

```text
...\LocalAIAgentWithRAG\.venv\Lib\site-packages\pip
```

This was important because:

```powershell
pip
```

can sometimes resolve differently depending on PATH configuration.

Using:

```powershell
python -m pip
```

ensures that pip is associated with the currently selected Python interpreter.

---

## 5. Direct Installation Test

A direct installation test was performed:

```powershell
python -m pip install requests
```

This successfully installed the package and demonstrated that:

* Python was functional.
* The virtual environment was functional.
* pip was functional.
* PyPI connectivity was functional.
* package installation into `.venv` was functional.

NumPy was subsequently tested:

```powershell
python -m pip install "numpy==2.3.5"
```

The package installed successfully under Python 3.13.15.

---

## 6. Requirements File Failure

The project contained:

```text
project_setup/requirements.txt
```

The command:

```powershell
python -m pip install -r .\project_setup\requirements.txt
```

appeared to execute successfully but did not install the expected project dependencies.

Investigation showed that the file was actually empty.

Its measured size was:

```text
Length: 0
```

and its content was:

```text
''
```

Therefore, pip was behaving correctly.

The dependency installation failure was not a pip failure.

---

## 7. Root Cause

The requirements file had not been persisted correctly from VS Code.

The causal chain was:

```text
Requirements edited
        ↓
File not saved
        ↓
requirements.txt remained empty
        ↓
pip received zero requirements
        ↓
No dependency installation occurred
```

The issue was resolved by restoring proper file saving/Auto Save behavior in VS Code.

---

## 8. Requirements Set

The intended project dependency specification included:

```text
langchain==1.3.15
langchain-core==1.5.4
langchain-community==0.4.2
langchain-ollama==1.1.0
langchain-chroma==1.1.0
langchain-text-splitters==1.1.2
chromadb==1.5.9
ollama==0.6.1
langsmith==0.11.0
langchain-classic==1.0.8
numpy==2.3.5
pandas==2.3.3
fastapi==0.116.1
flask==3.1.2
httpx==0.28.1
psycopg[binary]==3.2.10
PySide6==6.11.1
python-dotenv==1.2.0
python-docx==1.2.0
```

The complete dependency graph was subsequently installed into `.venv`.

---

## 9. Unnecessary Fixes Avoided

Several potentially destructive approaches were deliberately avoided:

* blindly uninstalling everything from global Python,
* deleting the virtual environment without evidence,
* randomly downgrading packages,
* reinstalling Python unnecessarily,
* modifying Windows PATH indiscriminately,
* assuming pip was broken,
* assuming the requirements resolver was broken.

The investigation instead established the state of each layer first.

---

## 10. General Engineering Lessons

### Lesson 1 — Interpreter identity matters

Always establish:

```text
Which Python?
Where is it?
Which pip?
Where are packages installed?
```

Useful commands:

```powershell
python --version
python -c "import sys; print(sys.executable)"
python -m pip --version
```

### Lesson 2 — Prefer interpreter-bound pip

Prefer:

```powershell
python -m pip install <package>
```

over relying blindly on:

```powershell
pip install <package>
```

### Lesson 3 — Validate configuration files

Before diagnosing a package manager, verify that the input file actually contains the expected configuration.

### Lesson 4 — The filesystem is part of the system

A development failure may originate from:

```text
Editor
   ↓
Filesystem
   ↓
Configuration
   ↓
Package manager
   ↓
Application
```

The application does not exist in isolation.

---

## 11. Diagnostic Method

```text
Symptom
  ↓
Verify active interpreter
  ↓
Verify pip
  ↓
Test direct package installation
  ↓
Inspect requirements file
  ↓
Discover file was empty
  ↓
Investigate why
  ↓
Restore file persistence
  ↓
Install dependencies
  ↓
Verify installed environment
```

## 12. Preventive Practice

Before troubleshooting dependency installation:

```powershell
python --version
python -c "import sys; print(sys.executable)"
python -m pip --version
Get-Content .\project_setup\requirements.txt
```

This establishes the environment before modifying it.
