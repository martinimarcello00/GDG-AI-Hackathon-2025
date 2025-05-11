const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { processUserQuery, getLatestResponseData } = require('./api'); // Updated imports
const fs = require('fs'); // Added fs module
const RESPONSE_FILE_PATH = path.join('/Users/danielelagana/github-sync/Hackathon/electron_ui/GDG-AI-Hackathon-2025/ui', 'response.json'); // Added response file path

let mainWindow;
let responseCheckInterval = null;

function createWindow() {
  const { screen } = require('electron');
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;
  
  // Initial compact dimensions - just enough for the chatbox
  const windowWidth = 375;
  const windowHeight = 160; // Just enough for the header and input box
  const screenWidth = width; // Store screen width to position window
  
  mainWindow = new BrowserWindow({
    width: windowWidth,
    height: windowHeight,
    x: screenWidth - windowWidth, // Position at the right edge
    y: height - windowHeight, // Position at the bottom
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'), // Optional for security
      nodeIntegration: true, // Needed if you're not using preload.js
      contextIsolation: false, // Disable if using nodeIntegration
    },
    frame: true, // Show window frame
    resizable: true, // Allow resizing
    minHeight: 160, // Minimum height to show the input
    minWidth: 320, // Minimum width
    maxWidth: 375, // Maximum width to maintain iPhone-like shape
  });

  mainWindow.loadFile('index.html');
  
  // Handle window close events
  mainWindow.on('close', () => {
    console.log('Window close event detected');
    
    // Clear interval if it's running
    if (responseCheckInterval) {
      clearInterval(responseCheckInterval);
    }
    
    app.quit(); // Force the app to quit
  });
}

ipcMain.handle('process-cv', async (_event, question) => {
  console.log('Received question:', question);

  try {
    // Clear any existing interval
    if (responseCheckInterval) {
      console.log('Clearing existing polling interval');
      clearInterval(responseCheckInterval);
      responseCheckInterval = null;
    }
    
    console.log('Starting Python script process for prompt:', question);
    
    // Start the Python script and get initial response
    // This will:
    // 1. Delete response.json if it exists
    // 2. Run client.py with the prompt
    // 3. Wait for response.json to be created and read it
    const initialResponse = await processUserQuery(question);
    console.log('Got initial response:', initialResponse);
    
    // Set up the polling interval to check for updates
    console.log('Setting up polling interval for response.json updates (every 5 seconds)');
    responseCheckInterval = setInterval(() => {
      try {
        // Get the latest data from response.json (if it exists)
        const latestData = getLatestResponseData();
        
        if (latestData && mainWindow && !mainWindow.isDestroyed()) {
          // Check if the data has actually changed
          const latestJSON = JSON.stringify(latestData);
          if (!this.lastSentData || this.lastSentData !== latestJSON) {
            console.log('Found updated data, sending to renderer');
            mainWindow.webContents.send('response-update', latestData);
            this.lastSentData = latestJSON;
          }
        }
      } catch (error) {
        console.error('Error in response check interval:', error);
      }
    }, 5000); // Check every 5 seconds
    
    return initialResponse;
  } catch (error) {
    console.error('Error during processing:', error);
    return { 
      followUp: 'Error processing your request.', 
      insights: 'Please try again later.',
      summary: ''
    };
  }
});

// Handle window resize requests from the renderer
ipcMain.on('resize-window', (_event, height) => {
  const { screen } = require('electron');
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width: screenWidth, height: screenHeight } = primaryDisplay.workAreaSize;
  
  console.log("Received resize request for height:", height);
  
  // Make sure the height is reasonable (between minimum and maximum allowed)
  const minHeight = 160; // Minimum height to show input
  const maxHeight = Math.floor(screenHeight * 0.8); // Maximum 80% of screen height
  const newHeight = Math.max(minHeight, Math.min(height, maxHeight));
  
  console.log("Setting new height to:", newHeight);
  
  // Get current position and size
  const [x, y] = mainWindow.getPosition();
  const [currentWidth] = mainWindow.getSize();
  
  // Update position to keep the window at the bottom edge of the screen
  mainWindow.setBounds({
    width: currentWidth, // Keep the same width
    height: newHeight,
    x: screenWidth - currentWidth, // Keep at right edge
    y: screenHeight - newHeight // Keep at bottom edge
  });
  
  // Log the new window size for debugging
  console.log("New window size:", mainWindow.getSize());
});

app.whenReady().then(() => {
  createWindow();
  
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

// Force quit the app when the window is closed (for all platforms including macOS)
app.on('window-all-closed', () => {
  console.log('All windows closed, quitting application...');
  
  // Clean up interval
  if (responseCheckInterval) {
    clearInterval(responseCheckInterval);
    responseCheckInterval = null;
  }
  
  // Note: We're not killing the python script because 
  // it's running a daemon process that we want to keep alive
  
  app.quit();
});

// Delete the response file when the app exits
app.on('quit', () => {
  console.log('Application quit, cleaning up resources...');
  
  // Clean up response.json if needed
  try {
    if (fs.existsSync(RESPONSE_FILE_PATH)) {
      fs.unlinkSync(RESPONSE_FILE_PATH);
      console.log('Cleaned up response.json file');
    }
  } catch (error) {
    console.error('Error cleaning up response.json:', error);
  }
});