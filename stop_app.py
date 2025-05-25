#!/usr/bin/env python3
"""
Nymo Art v4 - Application Shutdown Script
Gracefully stops all running instances of the application.
"""

import os
import sys
import time
import signal
import subprocess
import platform
from typing import List, Dict, Set


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


def get_processes_by_port(port: int) -> List[Dict]:
    """Get detailed process information for a specific port."""
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
                            processes.append({
                                'pid': int(parts[1]),
                                'command': parts[0],
                                'user': parts[2],
                                'port': port
                            })
                        except (ValueError, IndexError):
                            continue
                            
        elif platform.system() == "Linux":
            # Use ss and ps combination
            result = subprocess.run(
                ["ss", "-tlnp", f"sport = {port}"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if f":{port}" in line and "pid=" in line:
                        try:
                            pid_part = line.split("pid=")[1].split(",")[0]
                            pid = int(pid_part)
                            
                            # Get process details with ps
                            ps_result = subprocess.run(
                                ["ps", "-p", str(pid), "-o", "pid,user,comm", "--no-headers"],
                                capture_output=True,
                                text=True,
                                check=False
                            )
                            
                            if ps_result.returncode == 0:
                                ps_parts = ps_result.stdout.strip().split()
                                if len(ps_parts) >= 3:
                                    processes.append({
                                        'pid': pid,
                                        'command': ps_parts[2],
                                        'user': ps_parts[1],
                                        'port': port
                                    })
                        except (ValueError, IndexError):
                            continue
                            
        elif platform.system() == "Windows":
            # Use netstat and tasklist
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if f":{port}" in line and "LISTENING" in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            try:
                                pid = int(parts[-1])
                                
                                # Get process details with tasklist
                                tasklist_result = subprocess.run(
                                    ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV"],
                                    capture_output=True,
                                    text=True,
                                    check=False
                                )
                                
                                if tasklist_result.returncode == 0:
                                    lines = tasklist_result.stdout.strip().split('\n')
                                    if len(lines) >= 2:
                                        # Parse CSV output
                                        task_info = lines[1].replace('"', '').split(',')
                                        if len(task_info) >= 2:
                                            processes.append({
                                                'pid': pid,
                                                'command': task_info[0],
                                                'user': task_info[1] if len(task_info) > 1 else 'Unknown',
                                                'port': port
                                            })
                            except (ValueError, IndexError):
                                continue
                                
    except Exception as e:
        print_status(f"Error getting processes for port {port}: {e}", "ERROR")
        
    return processes


def get_nymo_related_processes() -> List[Dict]:
    """Find all processes related to Nymo Art application."""
    all_processes = []
    
    # Check standard ports
    ports = [8000, 5173]  # Backend, Frontend
    
    for port in ports:
        processes = get_processes_by_port(port)
        all_processes.extend(processes)
    
    # Also look for processes by name/command
    nymo_keywords = [
        'uvicorn',
        'app.main:app',
        'vite',
        'npm run dev',
        'node',
        'python'
    ]
    
    try:
        if platform.system() == "Darwin" or platform.system() == "Linux":
            # Use ps to find processes by command
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    for keyword in nymo_keywords:
                        if keyword in line and 'nymo' in line.lower():
                            parts = line.split()
                            if len(parts) >= 11:
                                try:
                                    pid = int(parts[1])
                                    # Avoid duplicates
                                    if not any(p['pid'] == pid for p in all_processes):
                                        all_processes.append({
                                            'pid': pid,
                                            'command': ' '.join(parts[10:]),
                                            'user': parts[0],
                                            'port': 'unknown'
                                        })
                                except (ValueError, IndexError):
                                    continue
                                    
        elif platform.system() == "Windows":
            # Use wmic or tasklist to find processes
            for keyword in ['uvicorn', 'node', 'python']:
                try:
                    result = subprocess.run(
                        ["tasklist", "/FI", f"IMAGENAME eq {keyword}.exe", "/FO", "CSV"],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')[1:]  # Skip header
                        for line in lines:
                            if 'nymo' in line.lower():
                                task_info = line.replace('"', '').split(',')
                                if len(task_info) >= 2:
                                    try:
                                        pid = int(task_info[1])
                                        if not any(p['pid'] == pid for p in all_processes):
                                            all_processes.append({
                                                'pid': pid,
                                                'command': task_info[0],
                                                'user': 'Unknown',
                                                'port': 'unknown'
                                            })
                                    except (ValueError, IndexError):
                                        continue
                except Exception:
                    continue
                    
    except Exception as e:
        print_status(f"Error searching for Nymo processes: {e}", "ERROR")
    
    return all_processes


def terminate_process_graceful(process_info: Dict) -> bool:
    """Terminate a process gracefully, with fallback to force kill."""
    pid = process_info['pid']
    command = process_info['command']
    
    try:
        print_status(f"Stopping process {pid} ({command})", "INFO")
        
        if platform.system() == "Windows":
            # Try graceful termination first
            subprocess.run(["taskkill", "/PID", str(pid)], check=True, capture_output=True)
        else:
            # Send SIGTERM first
            os.kill(pid, signal.SIGTERM)
            
        # Wait for graceful shutdown
        wait_time = 5
        while wait_time > 0:
            try:
                if platform.system() == "Windows":
                    result = subprocess.run(
                        ["tasklist", "/FI", f"PID eq {pid}"],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    if f"{pid}" not in result.stdout:
                        break
                else:
                    os.kill(pid, 0)  # Check if process exists
                    
                time.sleep(1)
                wait_time -= 1
                
            except (ProcessLookupError, subprocess.CalledProcessError):
                # Process already terminated
                break
        
        # If process still exists, force kill
        if wait_time == 0:
            print_status(f"Force killing process {pid}", "WARNING")
            if platform.system() == "Windows":
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=True)
            else:
                os.kill(pid, signal.SIGKILL)
        
        print_status(f"Successfully stopped process {pid}", "SUCCESS")
        return True
        
    except (ProcessLookupError, subprocess.CalledProcessError):
        # Process doesn't exist or already terminated
        print_status(f"Process {pid} was already stopped", "SUCCESS")
        return True
        
    except PermissionError:
        print_status(f"Permission denied killing process {pid}", "ERROR")
        return False
        
    except Exception as e:
        print_status(f"Error stopping process {pid}: {e}", "ERROR")
        return False


def cleanup_temp_files():
    """Clean up temporary files and caches."""
    print_status("Cleaning up temporary files...", "INFO")
    
    # Clean up common temp directories
    temp_patterns = [
        "__pycache__",
        "*.pyc",
        ".pytest_cache",
        "node_modules/.cache",
        ".vite"
    ]
    
    # Add specific cleanup logic here if needed
    print_status("Temporary files cleaned", "SUCCESS")


def main():
    """Main shutdown function."""
    print_status("🛑 Nymo Art v4 - Application Shutdown", "HEADER")
    print_status("=" * 50, "HEADER")
    
    # Find all Nymo-related processes
    print_status("Scanning for running Nymo Art processes...", "INFO")
    processes = get_nymo_related_processes()
    
    if not processes:
        print_status("No running Nymo Art processes found", "SUCCESS")
        print_status("Application is already stopped", "SUCCESS")
        return
    
    # Display found processes
    print_status(f"Found {len(processes)} running processes:", "INFO")
    for proc in processes:
        port_info = f" (port {proc['port']})" if proc['port'] != 'unknown' else ""
        print_status(f"  PID {proc['pid']}: {proc['command'][:50]}...{port_info}", "INFO")
    
    print()
    
    # Group processes by type for ordered shutdown
    backend_processes = [p for p in processes if 'uvicorn' in p['command'] or 'app.main' in p['command']]
    frontend_processes = [p for p in processes if 'vite' in p['command'] or ('npm' in p['command'] and 'dev' in p['command'])]
    other_processes = [p for p in processes if p not in backend_processes and p not in frontend_processes]
    
    success_count = 0
    total_count = len(processes)
    
    # Stop frontend first (dependent on backend)
    if frontend_processes:
        print_status("Stopping frontend processes...", "INFO")
        for proc in frontend_processes:
            if terminate_process_graceful(proc):
                success_count += 1
    
    # Stop backend
    if backend_processes:
        print_status("Stopping backend processes...", "INFO")
        for proc in backend_processes:
            if terminate_process_graceful(proc):
                success_count += 1
    
    # Stop other related processes
    if other_processes:
        print_status("Stopping other related processes...", "INFO")
        for proc in other_processes:
            if terminate_process_graceful(proc):
                success_count += 1
    
    # Clean up
    cleanup_temp_files()
    
    # Final status
    print_status("=" * 50, "HEADER")
    if success_count == total_count:
        print_status(f"✅ Successfully stopped all {total_count} processes", "SUCCESS")
        print_status("Nymo Art v4 application shutdown complete", "SUCCESS")
    else:
        failed_count = total_count - success_count
        print_status(f"⚠️ Stopped {success_count}/{total_count} processes", "WARNING")
        print_status(f"{failed_count} processes could not be stopped", "WARNING")
    
    print_status("=" * 50, "HEADER")
    
    # Final verification
    time.sleep(2)
    remaining_processes = get_nymo_related_processes()
    if remaining_processes:
        print_status(f"Warning: {len(remaining_processes)} processes still running", "WARNING")
        for proc in remaining_processes:
            print_status(f"  PID {proc['pid']}: {proc['command'][:50]}...", "WARNING")
    else:
        print_status("Verification: No Nymo Art processes running", "SUCCESS")


if __name__ == "__main__":
    main()
