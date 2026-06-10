# -*- coding: utf-8 -*-
import json
import os
import sys
import subprocess
from pathlib import Path

def find_large_files(min_size_mb=100):
    """查找大于指定大小的文件"""
    min_size_bytes = min_size_mb * 1024 * 1024
    
    # 获取所有驱动器
    drives = []
    result = subprocess.run(
        ['wmic', 'logicaldisk', 'get', 'DeviceID', '/format:csv'],
        capture_output=True,
        text=True
    )
    
    for line in result.stdout.split('\n')[1:]:
        parts = line.strip().split(',')
        if len(parts) >= 2 and parts[1]:
            device = parts[1].strip()
            if ':' in device:
                drives.append(device + '\\')
    
    large_files = []
    scanned_count = 0
    
    for drive in drives:
        if not os.path.exists(drive):
            continue
            
        try:
            for root, dirs, files in os.walk(drive):
                # 跳过系统目录
                if any(skip in root.lower() for skip in ['$recycle.bin', 'system volume information', 'windows\\winsxs']):
                    continue
                
                for filename in files:
                    filepath = os.path.join(root, filename)
                    try:
                        size = os.path.getsize(filepath)
                        if size >= min_size_bytes:
                            # 获取文件信息
                            stat = os.stat(filepath)
                            large_files.append({
                                'path': filepath,
                                'name': filename,
                                'size': size,
                                'sizeMB': round(size / 1024 / 1024, 2),
                                'modified': stat.st_mtime,
                                'folder': root
                            })
                            scanned_count += 1
                    except:
                        pass
                    
                    # 限制数量避免内存溢出
                    if scanned_count > 1000:
                        break
        except:
            pass
    
    # 按大小排序
    large_files.sort(key=lambda x: x['size'], reverse=True)
    
    return {
        'success': True,
        'files': large_files[:200],  # 最多返回200个
        'count': len(large_files),
        'minSizeMB': min_size_mb
    }

if __name__ == '__main__':
    min_size = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    print(json.dumps(find_large_files(min_size)))
