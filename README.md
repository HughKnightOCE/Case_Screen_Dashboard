# Case Screen Dashboard

A customizable dashboard application built with PySide6 Qt.

## Features

- Customizable 2x3 grid layout with configurable widgets
- Screen selection and layout presets
- Persistent configuration and state
- Widgets: university tasks, metrics, todo list, focus timer, logs

## Installation

Requires Python 3.8+.

```bash
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python main.py
```

On first run or with flags, the launcher will appear to select screen and layout.

- `--launcher`: Force show launcher
- `--pick`: Force show launcher

## Building

To create a standalone executable:

```bash
python build.py
```

## Testing

Run tests:

```bash
pytest
```

## Configuration

- `config.json`: Stores display index and layout preset
- `state.json`: Stores user data like todos
- `uni_tasks.json`: Stores university tasks

## Development

Follow `.github/copilot-instructions.md` for coding guidelines.