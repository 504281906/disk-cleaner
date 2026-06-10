const { app, BrowserWindow, ipcMain } = require('electron')
const path = require('path')
const { spawn } = require('child_process')

let win

function createWindow() {
  win = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    frame: true,
    backgroundColor: '#0f0f23',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  })

  if (process.env.VITE_DEV_SERVER_URL) {
    win.loadURL(process.env.VITE_DEV_SERVER_URL)
    win.webContents.openDevTools()
  } else {
    win.loadFile(path.join(__dirname, '../dist/index.html'))
  }
}

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

// IPC处理：调用Python后端
ipcMain.handle('run-python', async (event, { script, args = [] }) => {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(__dirname, '../backend', script)
    const argsStr = args.map(a => `"${a}"`).join(' ')
    
    const proc = spawn('python', [pythonScript, ...args], {
      shell: true,
      cwd: path.join(__dirname, '../backend')
    })

    let stdout = ''
    let stderr = ''

    proc.stdout.on('data', (data) => {
      stdout += data.toString()
    })

    proc.stderr.on('data', (data) => {
      stderr += data.toString()
    })

    proc.on('close', (code) => {
      if (code === 0) {
        try {
          resolve(JSON.parse(stdout))
        } catch {
          resolve({ success: true, data: stdout })
        }
      } else {
        reject(new Error(stderr || `Python script exited with code ${code}`))
      }
    })

    proc.on('error', (err) => {
      reject(err)
    })
  })
})
