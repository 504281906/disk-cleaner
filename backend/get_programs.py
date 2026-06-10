# -*- coding: utf-8 -*-
import json
import subprocess
import re

def get_installed_programs():
    """获取已安装程序列表"""
    programs = []
    
    try:
        # 使用PowerShell获取已安装程序
        result = subprocess.run(
            ['powershell', '-Command', 
             'Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* , HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* , HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* -ErrorAction SilentlyContinue | Select-Object DisplayName, DisplayVersion, Publisher, InstallDate, UninstallString | ConvertTo-Json'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.stdout:
            try:
                data = json.loads(result.stdout)
                if isinstance(data, dict):
                    data = [data]
                
                for item in data:
                    display_name = item.get('DisplayName', '')
                    if display_name and len(display_name) > 1:
                        programs.append({
                            'name': display_name,
                            'version': item.get('DisplayVersion', ''),
                            'publisher': item.get('Publisher', ''),
                            'installDate': item.get('InstallDate', ''),
                            'uninstallString': item.get('UninstallString', '')
                        })
            except json.JSONDecodeError:
                pass
    except Exception as e:
        pass
    
    # 按名称排序
    programs.sort(key=lambda x: x['name'].lower())
    
    return {'success': True, 'programs': programs}

if __name__ == '__main__':
    print(json.dumps(get_installed_programs()))
