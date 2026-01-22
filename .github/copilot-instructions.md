# Case Screen Dashboard - AI Coding Instructions

## Architecture Overview
This is a PySide6 Qt application for a customizable dashboard displayed on a specific screen. The app consists of:
- **app/**: Core logic (config, state, screens, main window)
- **ui/**: User interface components (dashboard, launcher, panels, widgets)
- **config.json**: Display index and widget layout configuration
- **state.json**: Persistent state (e.g., todos)

The dashboard uses a 2x3 grid layout with configurable slots for widgets: university, metrics, todo, focus_timer, logs, blank.

## Key Patterns
- **Configuration**: Use `AppConfig` dataclass with JSON persistence via `load_config()`/`save_config()`
- **State Management**: `AppState` dataclass for todos, persisted to `state.json`
- **UI Structure**: `QGridLayout` for dashboard, `Panel` base class for titled containers
- **Widgets**: Custom QWidget subclasses (e.g., `MetricTile`, `StatusList`)
- **Updates**: QTimer for periodic updates (e.g., metrics every 1s, logs every 10s)
- **Launcher**: Dialog for initial screen/layout selection, triggered on first run or `--launcher`/`--pick` flags

## Conventions
- Widget titles in lowercase (e.g., `title_label.setText(title.lower())`)
- Object names for styling (e.g., `setObjectName("panelTitle")`)
- Layout margins: 14px, spacing: 10px
- Fake data for development: Use sine waves for metrics simulation
- Imports: `from __future__ import annotations` for forward references

## Workflows
- **Run app**: `python main.py`
- **Force launcher**: `python main.py --launcher`
- **Pick screen**: `python main.py --pick`
- **Config persistence**: Automatic on launcher close
- **State persistence**: Automatic on app close (todos saved to `state.json`)
- **Test**: `pytest`
- **Build**: `python build.py`
- **Keyboard**: Ctrl+Q to quit

## Examples
- Add new widget: Extend `_make_widget()` in `DashboardView`, add to `WIDGET_TYPES` and `DEFAULT_LAYOUT`
- Update metrics: Call `dashboard.set_metrics(cpu_temp=val, gpu_load=val, ram_used=val)`
- Append log: `dashboard.append_log("message")`
- Load todos: `state = load_state(); dashboard.set_todos(state.todos)`
- Save todos: `todos = dashboard.get_todos(); state = AppState(todos=todos); save_state(state)`
- Load uni tasks: Edit `uni_tasks.json` manually
- Add tasks via launcher: Run `python main.py --launcher`, fill initial tasks fields
- Run tests: `pytest`
- Build executable: `python build.py`

## Notes
- Layout presets implemented in `app/config.py` with `PRESETS` dict (5 presets available)
- Missing widgets implemented: `UniTasksWidget`, `TodoListWidget`, `FocusTimerWidget` in `ui/widgets.py`
- State persistence wired to UI: load on startup, save on close in `app/window.py`
- Real system metrics: CPU/GPU load %, RAM used GB via `psutil`
- University tasks loaded from `uni_tasks.json`
- Keyboard shortcuts: Ctrl+Q to quit
- Tests in `tests/` directory
- Build script: `build.py` for PyInstaller executable

---

## 🔒 Architectural Rules (Strict – Must Follow)

These rules are non-negotiable and define how the dashboard must evolve.

- DO NOT hardcode layouts inside `DashboardView`
- DO NOT rewrite or restructure layouts unless explicitly requested
- Dashboard layout is **data-driven**, controlled by configuration and launcher choices
- `DashboardView` must only *consume* layout definitions, never define them

---

## 🧩 Widget Rules

- Each widget must:
  - Be a single `QWidget` subclass
  - Live in `ui/widgets.py` or its own widget file
  - Have one clear responsibility
  - Be independently usable
- Widgets must NOT:
  - Import or reference other widgets
  - Access `DashboardView` internals
  - Modify layouts directly
- Stateful widgets must expose:
  - `get_state()`
  - `set_state(state)`

---

## 🧱 Panel Rules

- Panels are **visual containers only**
- A panel:
  - Has a title
  - Wraps exactly ONE widget
- Panels handle:
  - Margins
  - Spacing
  - Title rendering
- Panels do NOT contain business logic

---

## 🚀 Launcher Rules

- The launcher controls:
  - Which screen the app opens on
  - Which layout preset is used
  - (Future) Which widget goes into which slot
  - Initial tasks setup for university and todo widgets
- The launcher:
  - Outputs configuration data only
  - Does NOT instantiate widgets
  - Does NOT modify UI layout code directly
  - Can append initial tasks to state and uni_tasks.json

---

## 💾 State & Config Rules

- `config.json` stores:
  - Display index
  - Selected layout preset
  - Widget-slot mappings (future)
- `state.json` stores:
  - User data (todos, university tasks, timer state)
- Widgets are responsible for reading/writing their own state via exposed methods
- State persistence must not be embedded into layout code

---

## ✋ Coding Constraints

- NEVER change UI styling unless explicitly requested
- NEVER refactor working code unless explicitly requested
- ALWAYS provide full-file replacements when modifying code
- Prefer registries and configuration over conditionals
- Avoid hidden side effects or silent behavior changes

---

## 🧠 Design Philosophy

This application is a **configurable dashboard framework**, not a static UI.

Adding features should mean:
- Registering new widgets
- Updating configuration
- Selecting layouts via launcher

NOT:
- Rewriting layouts
- Duplicating code
- Hardcoding widget placement

---

## 🔌 Extension Pattern (Required)

To add a new widget:
1. Create the widget class
2. Register it in a widget registry
3. Assign it to a layout slot via configuration
4. Do NOT modify `DashboardView` layout code
