# Case Screen Dashboard

A personalized dashboard for the HYTE Y70ti PC case

## Background & Motivation

This project was created to address the limitations of the stock HYTE software for the Y70ti PC case. The default software offered only basic system monitoring and limited customisation, which didn't fit my workflow or aesthetic preferences.

I wanted a dashboard that would:
- Be minimalistic and visually clean
- Help me stay on top of day-to-day tasks
- Track university assignments and deadlines
- Provide a focus timer and productivity tools
- Allow full control over layout and widgets

The Case Screen Dashboard is designed to run on the Y70ti's built-in display, but works on any monitor. It is fully data-driven, so you can swap widgets, change layouts, and personalise the experience to suit your needs.

**Why?**
I built this because I wanted my PC case display to be genuinely useful—not just a system monitor or RGB gimmick. This dashboard helps me keep organized, focused, and motivated throughout the day, especially for university work and personal productivity.

If you have a Y70ti (or any case with a display), you can use this project to create your own personalized dashboard.
A customizable dashboard application built with PySide6 Qt.

## Features


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
