# -*- coding: utf-8 -*-
import json
import os
import subprocess
import re
from pathlib import Path

def get_temp_files():
    """获取临时文件"""
    temp_paths = [
        os.getenv('TEMP', ''),
        os.path.join(os.getenv('WINDIR', 'C:\\Windows'), 'Temp'),
        os.path.join(os.getenv('LOCALAPPDATA', ''), 'Temp')
    ]
    
    files = []
    total_size = 0
    
    for temp_path in temp_paths:
        if os.path.exists(temp_path):
            try:
                for root, dirs, filenames in os.walk(temp_path):
                    for filename in filenames:
                        filepath = os.path.join(root, filename)
                        try:
                            size = os.path.getsize(filepath)
                            total_size += size
                            files.append({
                                'path': filepath,
                                'size': size,
                                'type': 'temp'
                            })
                        except:
                            pass
            except:
                pass
    
    return files, total_size

def get_browser_cache():
    """获取浏览器缓存"""
    appdata = os.getenv('APPDATA', '')
    localappdata = os.getenv('LOCALAPPDATA', '')
    
    browser_paths = [
        os.path.join(localappdata, 'Google', 'Chrome', 'User Data', 'Default', 'Cache'),
        os.path.join(localappdata, 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache'),
        os.path.join(localappdata, 'Mozilla', 'Firefox', 'Profiles'),
        os.path.join(appdata, 'Opera Software', 'Opera Stable', 'Cache')
    ]
    
    files = []
    total_size = 0
    
    for bpath in browser_paths:
        if os.path.exists(bpath):
            try:
                for root, dirs, filenames in os.walk(bpath):
                    for filename in filenames:
                        filepath = os.path.join(root, filename)
                        try:
                            size = os.path.getsize(filepath)
                            total_size += size
                            files.append({
                                'path': filepath,
                                'size': size,
                                'type': 'browser_cache'
                            })
                        except:
                            pass
            except:
                pass
    
    return files, total_size

def get_recycle_bin_size():
    """获取回收站大小"""
    try:
        # 获取回收站信息
        result = subprocess.run(
            ['powershell', '-Command', 
             '[System.IO.File]::GetLogicalDrives() | ForEach-Object { $_.ToString() }'],
            capture_output=True,
            text=True
        )
        
        recycle_size = 0
        recycle_count = 0
        
        for letter in ['C:', 'D:', 'E:']:
            try:
                result = subprocess.run(
                    ['powershell', '-Command', 
                     f'Clear-RecycleBin -DriveLetter "{letter[0]}" -Confirm:$false -ErrorAction SilentlyContinue; (New-Object -ComObject Shell.Application).NameSpace(0x0a).ParseName("{letter}\\$Recycle.Bin").GetDetailsOf(0)'],
                    capture_output=True,
                    text=True
                )
            except:
                pass
        
        return recycle_size, recycle_count
    except:
        return 0, 0

def get_log_files():
    """获取日志文件"""
    windows_dir = os.getenv('WINDIR', 'C:\\Windows')
    log_paths = [
        os.path.join(windows_dir, 'Logs'),
        os.path.join(windows_dir, 'Panther'),
        os.path.join(os.getenv('LOCALAPPDATA', ''), 'CrashDumps')
    ]
    
    files = []
    total_size = 0
    
    for lpath in log_paths:
        if os.path.exists(lpath):
            try:
                for root, dirs, filenames in os.walk(lpath):
                    for filename in filenames:
                        filepath = os.path.join(root, filename)
                        try:
                            size = os.path.getsize(filepath)
                            total_size += size
                            files.append({
                                'path': filepath,
                                'size': size,
                                'type': 'log'
                            })
                        except:
                            pass
            except:
                pass
    
    return files, total_size

def scan_garbage():
    """扫描垃圾文件"""
    results = {
        'temp': {'name': '临时文件', 'files': [], 'size': 0},
        'browser_cache': {'name': '浏览器缓存', 'files': [], 'size': 0},
        'log': {'name': '日志文件', 'files': [], 'size': 0}
    }
    
    # 扫描临时文件
    temp_files, temp_size = get_temp_files()
    results['temp']['files'] = temp_files[:100]  # 限制数量
    results['temp']['size'] = temp_size
    
    # 扫描浏览器缓存
    browser_files, browser_size = get_browser_cache()
    results['browser_cache']['files'] = browser_files[:100]
    results['browser_cache']['size'] = browser_size
    
    # 扫描日志文件
    log_files, log_size = get_log_files()
    results['log']['files'] = log_files[:50]
    results['log']['size'] = log_size
    
    # 计算总大小
    total_size = temp_size + browser_size + log_size
    
    return {
        'success': True,
        'categories': results,
        'totalSize': total_size
    }

if __name__ == '__main__':
    print(json.dumps(scan_garbage()))
