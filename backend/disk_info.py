# -*- coding: utf-8 -*-
import json
import subprocess
import re

def get_disk_info():
    """获取磁盘信息"""
    try:
        # 使用wmic获取磁盘信息
        result = subprocess.run(
            ['wmic', 'logicaldisk', 'get', 'DeviceID,FreeSpace,Size,VolumeName', '/format:csv'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        lines = result.stdout.strip().split('\n')
        disks = []
        
        for line in lines[1:]:  # 跳过表头
            parts = line.strip().split(',')
            if len(parts) >= 4 and parts[1]:  # DeviceID
                device_id = parts[1].strip()
                if ':' in device_id:
                    free_space = int(parts[2].strip()) if parts[2].strip() else 0
                    size = int(parts[3].strip()) if parts[3].strip() else 0
                    volume_name = parts[4].strip() if len(parts) > 4 else ''
                    
                    if size > 0:
                        used = size - free_space
                        disks.append({
                            'device': device_id,
                            'volumeName': volume_name or device_id,
                            'total': size,
                            'free': free_space,
                            'used': used,
                            'percent': round(used / size * 100, 1)
                        })
        
        return {'success': True, 'disks': disks}
    except Exception as e:
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    print(json.dumps(get_disk_info()))
