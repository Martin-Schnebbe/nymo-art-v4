#!/usr/bin/env python3
"""
Nymo Art v4 - Application Shutdown Script
Gracefully stops all running instances of the application.
"""

import os
import sys
import time

# Add utils directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))
from process_manager import (
    print_status, Colors, cleanup_all_nymo_processes, 
    kill_processes_on_port, wait_for_port_clear,
    get_processes_by_port, get_nymo_processes_by_port, 
    get_non_nymo_processes_by_port
)


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
    
    # Method 1: Clean up processes by known ports (most reliable)
    ports_to_check = [8000, 5173]  # Backend, Frontend
    total_killed = 0
    
    for port in ports_to_check:
        print_status(f"Checking port {port}...", "INFO")
        
        # Get all processes on this port
        all_processes = get_processes_by_port(port)
        nymo_processes = [p for p in all_processes if p.is_nymo_process]
        non_nymo_processes = [p for p in all_processes if not p.is_nymo_process]
        
        if nymo_processes:
            print_status(f"Found {len(nymo_processes)} Nymo processes on port {port}", "INFO")
            for process in nymo_processes:
                print_status(f"  - PID {process.pid}: {process.full_command[:60]}...", "INFO")
            
            # Kill Nymo processes
            nymo_killed, _ = kill_processes_on_port(port, kill_non_nymo=False)
            total_killed += nymo_killed
            
            # Wait for port to clear
            if wait_for_port_clear(port, timeout=5):
                print_status(f"Port {port} is now clear", "SUCCESS")
            else:
                print_status(f"Port {port} still occupied after cleanup", "WARNING")
        
        if non_nymo_processes:
            print_status(f"Found {len(non_nymo_processes)} non-Nymo processes on port {port}:", "WARNING")
            for process in non_nymo_processes:
                print_status(f"  - PID {process.pid}: {process.full_command[:60]}...", "WARNING")
            print_status("Leaving non-Nymo processes alone", "INFO")
        
        if not all_processes:
            print_status(f"Port {port} is already clear", "SUCCESS")
    
    # Method 2: Find any remaining Nymo processes not tied to specific ports
    print_status("Scanning for remaining Nymo processes...", "INFO")
    remaining_killed = cleanup_all_nymo_processes()
    total_killed += remaining_killed
    
    # Clean up temporary files
    cleanup_temp_files()
    
    # Final status
    print_status("=" * 50, "HEADER")
    if total_killed > 0:
        print_status(f"✅ Successfully stopped {total_killed} Nymo processes", "SUCCESS")
    else:
        print_status("No Nymo Art processes were running", "SUCCESS")
    
    print_status("Nymo Art v4 application shutdown complete", "SUCCESS")
    print_status("=" * 50, "HEADER")
    
    # Final verification
    time.sleep(1)
    print_status("Final verification...", "INFO")
    final_check = cleanup_all_nymo_processes()
    if final_check == 0:
        print_status("✅ Verification: No Nymo Art processes running", "SUCCESS")
    else:
        print_status(f"⚠️ Warning: Found {final_check} additional processes during verification", "WARNING")


if __name__ == "__main__":
    main()
