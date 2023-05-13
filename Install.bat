@echo off
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo Failed to upgrade pip
    pause
) else (
    pip install paramiko tqdm
    if %errorlevel% neq 0 (
        echo Failed to install libraries
        pause
    ) else (
        echo All good
        pause
    )
)
