
# ExileLedger - PoE2 Automated Market Arbitrage Analyzer

`ExileLedger` is a modular standalone analytical tool tailored for Path of Exile 2 trade site mechanics. It evaluates raw profit margins, optimizes listing quantities against integer trading constraints, and tracks systemic gold-sink overhead friction across currency flips.

## 💡 Core Features

* **Multi-Variable Integer Matching Engine**: Evaluates both buy and sell values simultaneously (supporting fractions like `1.5/1` or decimals like `1.55`). It scales fraction values up to the lowest common integers, giving you realistic bulk trading instructions that can actually be listed on the market.
* **/D Normalized Gold Friction Metrics**: Automatically scales multi-tier listing taxes down to a normalized baseline of 1 pure Divine net profit, showing you the exact gold cost required to earn 1 net D.
* **Persistent Snapshot Profiles**: Saves local data structures to a local JSON payload (`storage.json`). Values are saved across application sessions and can be loaded back into the active workspace with a single click.
* **Real-time Algebra Logging**: Features a collapsible analytical trace log detailing the precise mathematical step-by-step processing paths.

## 📁 File Structure

* `config.py`: Single Source of Truth for visual theme dictionaries, data persistence variables, and fallback baselines.
* `calc_engine.py`: Isolated mathematical matrix layer. Runs independently of UI bindings.
* `ui_components.py`: Houses custom composite layout elements (e.g., the collapsible logging view terminal).
* `main.py`: Central orchestrator linking UI element events to engine calculations and JSON read/write hooks.
* `build_exe.py`: DevOps compilation configuration to compile code into a standalone binary distribution.

## 🛠️ Developer Operations

### 1. Prerequisite Checks
The application relies strictly on Python's native standard library modules (`tkinter`, `json`, `os`). The only exterior requirement is `pyinstaller`, and that is only needed if you are building an executable binary.

```bash
pip install pyinstaller
```
2. Run Local Source Code
```bash
python main.py
```
3. Compile Standalone Desktop Target (.exe)
Run the provided build automation script to build a compressed distribution bundle:

```bash
python build_exe.py
```
Once the build completes successfully, find the executable utility inside the target path: ./dist/ExileLedger.exe.