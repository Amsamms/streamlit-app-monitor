@echo off
REM 1) Activate the conda environment
call conda activate depi_project_3.12

REM 2) Run the Python script and record output in streamlit_monitor.log
python "C:\Users\Estabrk\Cursor AI Projects\My web_apps\Automating web apps\streamlit_app_monitor.py"
