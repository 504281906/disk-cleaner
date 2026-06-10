# -*- coding: utf-8 -*-
import json
import os
import sys

def clean_files(paths):
    """清理指定文件"""
    if not paths:
        return {'success': True, 'cleaned': 0, 'failed': 0, 'size': 0}
    
    cleaned = 0
    failed = 0
    total_size = 0
    
    for filepath in paths:
        try:
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                os.remove(filepath)
                cleaned += 1
                total_size += size
        except Exception as e:
            failed += 1
    
    return {
        'success': True,
        'cleaned': cleaned,
        'failed': failed,
        'size': total_size
    }

if __name__ == '__main__':
    # 从命令行参数获取要清理的文件列表
    if len(sys.argv) > 1:
        # JSON格式的文件路径列表
        try:
            paths = json.loads(sys.argv[1])
            result = clean_files(paths)
            print(json.dumps(result))
        except:
            print(json.dumps({'success': False, 'error': 'Invalid paths format'}))
    else:
        print(json.dumps({'success': True, 'cleaned': 0, 'failed': 0, 'size': 0}))
