# -*- coding: utf-8 -*-
import json
import subprocess
import sys
import os

def uninstall_program(program_name):
    """卸载指定程序"""
    if not program_name:
        return {'success': False, 'error': 'No program specified'}
    
    try:
        # 先尝试使用MSI卸载
        result = subprocess.run(
            ['powershell', '-Command', 
             f'Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* , HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* -ErrorAction SilentlyContinue | Where-Object {{ $_.DisplayName -eq "{program_name}" }} | Select-Object UninstallString'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        uninstall_string = result.stdout.strip()
        
        if uninstall_string:
            # 执行卸载命令
            if 'MsiExec' in uninstall_string:
                # MSI卸载
                match = re.search(r'MsiExec\.exe\s+/[IXxuZ](\{[A-F0-9-]+\})', uninstall_string, re.IGNORECASE)
                if match:
                    guid = match.group(1)
                    proc = subprocess.run(
                        ['msiexec', '/x', guid, '/quiet', '/norestart'],
                        capture_output=True,
                        text=True
                    )
            else:
                # 普通卸载
                proc = subprocess.Popen(
                    uninstall_string,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True
                )
                proc.wait(timeout=120)
            
            return {'success': True, 'message': f'Uninstallation started for {program_name}'}
        else:
            return {'success': False, 'error': 'Program not found in registry'}
    
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'Uninstallation timed out'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    if len(sys.argv) > 1:
        program = ' '.join(sys.argv[1:])
        print(json.dumps(uninstall_program(program)))
    else:
        print(json.dumps({'success': False, 'error': 'No program specified'}))
