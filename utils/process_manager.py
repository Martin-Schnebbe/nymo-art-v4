#!/usr/bin/env python3
"""
Nymo Art v4 - Shared Process Management Utilities
Provides common functionality for process detection, management, and cleanup.
"""

import os
import sys
import time
import signal
import subprocess
import platform
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_status(message: str, status: str = "INFO") -> None:
    """Print formatted status message."""
    colors = {
        "INFO": Colors.OKBLUE,
        "SUCCESS": Colors.OKGREEN,
        "WARNING": Colors.WARNING,
        "ERROR": Colors.FAIL,
        "HEADER": Colors.HEADER
    }
    color = colors.get(status, Colors.OKBLUE)
    print(f"{color}[{status}]{Colors.ENDC} {message}")


class ProcessInfo:
    """Container for process information."""
    def __init__(self, pid: int, command: str, full_command: str, working_dir: str, port: Optional[int] = None):
        self.pid = pid
        self.command = command
        self.full_command = full_command
        self.working_dir = working_dir
        self.port = port
        self.is_nymo_process = self._is_nymo_process()
    
    def _is_nymo_process(self) -> bool:
        """Determine if this is a legitimate Nymo Art process using ultra-specific criteria."""
        project_path = get_project_path()
        
        # 🚫 EXCLUSIONS: Never consider these as Nymo processes
        exclusions = [
            "start_app.py" in self.full_command,
            "stop_app.py" in self.full_command,
            "test_" in self.full_command,
            "pytest" in self.full_command,
            "__pycache__" in self.full_command,
        ]
        
        if any(exclusions):
            return False
        
        # 🔥 ULTRA-SPECIFIC Nymo process detection
        nymo_indicators = [
            # Backend patterns - must have both command AND project path verification
            (
                ("uvicorn app.main:app" in self.full_command or "app.main:app" in self.full_command) and
                (project_path in self.full_command or self.working_dir == project_path)
            ),
            
            # Frontend patterns - must include our specific project path in command
            (
                "npm run dev" in self.full_command and 
                f"{project_path}/frontend" in self.full_command
            ),
            
            # Node.js patterns - must be in our frontend directory
            (
                ("node" in self.command.lower() or "vite" in self.full_command) and
                (self.working_dir.startswith(f"{project_path}/frontend") or 
                 f"{project_path}/frontend" in self.full_command) and
                (self.port is not None and self.port == 5173 or "dev" in self.full_command)
            ),
            
            # Python patterns - must be in our project directory with app-related commands (but not management scripts)
            (
                "python" in self.command.lower() and
                project_path in self.working_dir and
                ("app" in self.full_command or "main" in self.full_command or "uvicorn" in self.full_command) and
                not any(script in self.full_command for script in ["start_app.py", "stop_app.py", "test_"])
            )
        ]
        
        return any(nymo_indicators)
    
    def __repr__(self):
        return f"ProcessInfo(pid={self.pid}, command='{self.command}', is_nymo={self.is_nymo_process})"


def get_project_path() -> str:
    """Get the project path."""
    return "/Users/schnebbe/Library/Mobile Documents/com~apple~CloudDocs/01 Nymo/03_NymoArt/30 Scripts/nymo art v4"


def get_process_details(pid: int) -> Tuple[str, str]:
    """Get full command line and working directory for a process."""
    try:
        # Get full command line
        ps_result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "args="],
            capture_output=True,
            text=True,
            check=False
        )
        
        full_command = ps_result.stdout.strip() if ps_result.returncode == 0 else ""
        
        # Get working directory using lsof (more reliable than pwdx on macOS)
        lsof_result = subprocess.run(
            ["lsof", "-p", str(pid)],
            capture_output=True,
            text=True,
            check=False
        )
        
        working_dir = ""
        project_path = get_project_path()
        
        if lsof_result.returncode == 0:
            for line in lsof_result.stdout.split('\n'):
                if "cwd" in line:
                    # Extract directory from lsof output
                    # Format: COMMAND PID USER FD TYPE DEVICE SIZE/OFF NODE NAME
                    parts = line.split()
                    if len(parts) >= 9:
                        potential_dir = " ".join(parts[8:])  # Join in case path has spaces
                        if os.path.isdir(potential_dir):
                            working_dir = potential_dir
                            break
        
        return full_command, working_dir
        
    except Exception as e:
        print_status(f"Error getting process details for PID {pid}: {e}", "WARNING")
        return "", ""


def get_processes_by_port(port: int) -> List[ProcessInfo]:
    """Get all processes using a specific port, with Nymo/non-Nymo classification."""
    processes = []
    
    try:
        if platform.system() == "Darwin":  # macOS
            # Use lsof to get detailed process info
            result = subprocess.run(
                ["lsof", "-i", f":{port}", "-P"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 10:
                        try:
                            pid = int(parts[1])
                            command = parts[0]
                            
                            # Get detailed process information
                            full_command, working_dir = get_process_details(pid)
                            
                            process_info = ProcessInfo(
                                pid=pid,
                                command=command,
                                full_command=full_command,
                                working_dir=working_dir,
                                port=port
                            )
                            
                            processes.append(process_info)
                            
                        except (ValueError, IndexError) as e:
                            print_status(f"Error parsing lsof line: {line} - {e}", "WARNING")
        else:
            # Linux/other systems
            result = subprocess.run(
                ["netstat", "-tulpn"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if f":{port}" in line and "LISTEN" in line:
                        # Extract PID from netstat output
                        parts = line.split()
                        if len(parts) >= 7:
                            pid_info = parts[6]
                            if '/' in pid_info:
                                try:
                                    pid = int(pid_info.split('/')[0])
                                    command = pid_info.split('/')[1]
                                    
                                    full_command, working_dir = get_process_details(pid)
                                    
                                    process_info = ProcessInfo(
                                        pid=pid,
                                        command=command,
                                        full_command=full_command,
                                        working_dir=working_dir,
                                        port=port
                                    )
                                    
                                    processes.append(process_info)
                                    
                                except (ValueError, IndexError) as e:
                                    print_status(f"Error parsing netstat line: {line} - {e}", "WARNING")
    
    except Exception as e:
        print_status(f"Error checking port {port}: {e}", "ERROR")
    
    return processes


def get_nymo_processes_by_port(port: int) -> List[ProcessInfo]:
    """Get only Nymo processes using a specific port."""
    all_processes = get_processes_by_port(port)
    return [p for p in all_processes if p.is_nymo_process]


def get_non_nymo_processes_by_port(port: int) -> List[ProcessInfo]:
    """Get only non-Nymo processes using a specific port."""
    all_processes = get_processes_by_port(port)
    return [p for p in all_processes if not p.is_nymo_process]


def kill_process(process_info: ProcessInfo, signal_type: int = signal.SIGTERM) -> bool:
    """Safely terminate a process."""
    try:
        print_status(f"Terminating process {process_info.pid} ({process_info.command})", "INFO")
        
        # Send the signal
        os.kill(process_info.pid, signal_type)
        
        # Wait a bit for graceful shutdown
        time.sleep(1)
        
        # Check if process is still running
        try:
            os.kill(process_info.pid, 0)  # Signal 0 just checks if process exists
            if signal_type == signal.SIGTERM:
                # Process still running, try SIGKILL
                print_status(f"Process {process_info.pid} still running, sending SIGKILL", "WARNING")
                os.kill(process_info.pid, signal.SIGKILL)
                time.sleep(0.5)
        except ProcessLookupError:
            # Process is gone, which is what we want
            pass
        
        print_status(f"Successfully terminated process {process_info.pid}", "SUCCESS")
        return True
        
    except ProcessLookupError:
        print_status(f"Process {process_info.pid} was already terminated", "INFO")
        return True
    except PermissionError:
        print_status(f"Permission denied to terminate process {process_info.pid}", "ERROR")
        return False
    except Exception as e:
        print_status(f"Error terminating process {process_info.pid}: {e}", "ERROR")
        return False


def kill_processes_on_port(port: int, kill_non_nymo: bool = False) -> Tuple[int, int]:
    """
    Kill processes on a specific port.
    
    Args:
        port: Port number to clear
        kill_non_nymo: If True, also kill non-Nymo processes (with warning)
    
    Returns:
        Tuple of (nymo_processes_killed, non_nymo_processes_killed)
    """
    all_processes = get_processes_by_port(port)
    nymo_processes = [p for p in all_processes if p.is_nymo_process]
    non_nymo_processes = [p for p in all_processes if not p.is_nymo_process]
    
    nymo_killed = 0
    non_nymo_killed = 0
    
    # Always kill Nymo processes
    for process in nymo_processes:
        if kill_process(process):
            nymo_killed += 1
    
    # Handle non-Nymo processes
    if non_nymo_processes:
        if kill_non_nymo:
            print_status(f"WARNING: Found {len(non_nymo_processes)} non-Nymo processes on port {port}:", "WARNING")
            for process in non_nymo_processes:
                print_status(f"  - PID {process.pid}: {process.full_command}", "WARNING")
            
            response = input(f"Kill these non-Nymo processes? (y/N): ").strip().lower()
            if response == 'y':
                for process in non_nymo_processes:
                    if kill_process(process):
                        non_nymo_killed += 1
            else:
                print_status("Skipping non-Nymo processes", "INFO")
        else:
            print_status(f"Found {len(non_nymo_processes)} non-Nymo processes on port {port} (leaving them alone):", "INFO")
            for process in non_nymo_processes:
                print_status(f"  - PID {process.pid}: {process.full_command}", "INFO")
    
    return nymo_killed, non_nymo_killed


def is_port_available(port: int) -> bool:
    """Check if a port is available (no processes using it)."""
    processes = get_processes_by_port(port)
    return len(processes) == 0


def wait_for_port_clear(port: int, timeout: int = 10) -> bool:
    """Wait for a port to become available."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_available(port):
            return True
        time.sleep(0.5)
    return False


def find_nymo_processes() -> List[ProcessInfo]:
    """Find all running Nymo processes (not tied to specific ports)."""
    processes = []
    project_path = get_project_path()
    
    try:
        # Get all running processes
        if platform.system() == "Darwin":  # macOS
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                check=False
            )
        else:  # Linux
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                check=False
            )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            for line in lines:
                parts = line.split(None, 10)  # Split on whitespace, max 11 parts
                if len(parts) >= 11:
                    try:
                        pid = int(parts[1])
                        command = parts[10]  # Full command line
                        
                        # Quick filter - only check processes that might be related
                        if any(keyword in command.lower() for keyword in ['uvicorn', 'node', 'npm', 'vite', 'python']):
                            full_command, working_dir = get_process_details(pid)
                            
                            process_info = ProcessInfo(
                                pid=pid,
                                command=parts[10].split()[0] if parts[10] else "",
                                full_command=full_command,
                                working_dir=working_dir
                            )
                            
                            if process_info.is_nymo_process:
                                processes.append(process_info)
                                
                    except (ValueError, IndexError):
                        continue
    
    except Exception as e:
        print_status(f"Error finding Nymo processes: {e}", "ERROR")
    
    return processes


def cleanup_all_nymo_processes() -> int:
    """Find and terminate all Nymo processes."""
    processes = find_nymo_processes()
    killed_count = 0
    
    if not processes:
        print_status("No running Nymo processes found", "INFO")
        return 0
    
    print_status(f"Found {len(processes)} Nymo processes:", "INFO")
    for process in processes:
        print_status(f"  - PID {process.pid}: {process.full_command}", "INFO")
    
    for process in processes:
        if kill_process(process):
            killed_count += 1
    
    return killed_count
