const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  // 调用Python后端脚本
  runPython: (script, args = []) => ipcRenderer.invoke('run-python', { script, args }),
  
  // 获取磁盘信息
  getDiskInfo: () => ipcRenderer.invoke('run-python', { 
    script: 'disk_info.py', 
    args: [] 
  }),
  
  // 扫描垃圾文件
  scanGarbage: () => ipcRenderer.invoke('run-python', { 
    script: 'scan_garbage.py', 
    args: [] 
  }),
  
  // 清理垃圾
  cleanGarbage: (paths) => ipcRenderer.invoke('run-python', { 
    script: 'clean_garbage.py', 
    args: [paths] 
  }),
  
  // 获取已安装程序
  getPrograms: () => ipcRenderer.invoke('run-python', { 
    script: 'get_programs.py', 
    args: [] 
  }),
  
  // 卸载程序
  uninstallProgram: (programName) => ipcRenderer.invoke('run-python', { 
    script: 'uninstall.py', 
    args: [programName] 
  }),
  
  // 查找大文件
  findLargeFiles: (minSizeMB = 100) => ipcRenderer.invoke('run-python', { 
    script: 'find_large_files.py', 
    args: [String(minSizeMB)] 
  })
})
