const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

// Path to the response.json file (client.py writes to this file)
const RESPONSE_FILE_PATH = path.join(__dirname, '', 'response.json');

// Function to delete response.json if it exists
function deleteResponseFileIfExists() {
  if (fs.existsSync(RESPONSE_FILE_PATH)) {
    try {
      fs.unlinkSync(RESPONSE_FILE_PATH);
      console.log('Existing response.json file deleted');
    } catch (error) {
      console.error('Error deleting response.json file:', error);
    }
  }
}

// Function to check if a file exists
function fileExists(filePath) {
  try {
    return fs.existsSync(filePath);
  } catch (error) {
    console.error(`Error checking if file exists (${filePath}):`, error);
    return false;
  }
}

// Function to spawn the Python script with the user's prompt
function runPythonScript(prompt) {
  return new Promise((resolve, reject) => {
    console.log('Spawning Python process with prompt:', prompt);
    
    // Define the path to the Python script (using the existing client.py)
    const pythonScriptPath = path.join(__dirname, '..', 'client.py');
    
    // Check if the Python script exists
    if (!fileExists(pythonScriptPath)) {
      console.error(`Python script not found at: ${pythonScriptPath}`);
      return reject(new Error(`Python script not found at: ${pythonScriptPath}`));
    }
    
    console.log(`Found Python script at: ${pythonScriptPath}`);
    
    // Spawn the Python process with the prompt as an argument
    // Use the --prompt flag as specified in client.py
    console.log('Command to run:', 'python3', [pythonScriptPath, '--prompt', prompt]);
    const pythonProcess = spawn('python3', [pythonScriptPath, '--prompt', prompt]);
    
    // Track stdout data for session creation message
    let stdoutData = '';
    let stderrData = '';
    
    // Log output from the Python script
    pythonProcess.stdout.on('data', (data) => {
      const output = data.toString();
      console.log(`Python script output: ${output}`);
      stdoutData += output;
      
      // Check if we've received the session creation message
      if (stdoutData.includes('Session created successfully')) {
        // Once we see the session creation message, we can consider the initial setup done
        // This doesn't wait for the entire process to finish since it runs a daemon
        resolve();
      }
    });
    
    // Log error output from the Python script
    pythonProcess.stderr.on('data', (data) => {
      const output = data.toString();
      console.error(`Python script error: ${output}`);
      stderrData += output;
    });
    
    // Handle process completion
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.error(`Python process exited with code ${code}`);
        // Don't reject here, as the daemon will continue to run
      } else {
        console.log('Python process completed successfully');
      }
    });
    
    // Handle process errors
    pythonProcess.on('error', (err) => {
      console.error('Failed to start Python process:', err);
      reject(new Error(`Failed to start Python process: ${err.message}`));
    });
    
    // Set a timeout to resolve the promise if we don't see the expected output
    // This is a fallback to ensure we don't hang
    setTimeout(() => {
      if (!stdoutData.includes('Session created successfully')) {
        console.log('Timeout waiting for "Session created successfully" message, resolving anyway');
        resolve();
      }
    }, 10000); // 10 second timeout
  });
}

// Function to check for and read response.json file
function checkForResponseFile() {
  return new Promise((resolve, reject) => {
    try {
      const filePath = RESPONSE_FILE_PATH;
      const exists = fs.existsSync(filePath);
      
      if (exists) {
        console.log(`Response file exists at: ${filePath}`);
        try {
          const data = fs.readFileSync(filePath, 'utf8');
          try {
            const jsonData = JSON.parse(data);
            console.log('Successfully parsed response.json data');
            resolve(jsonData);
          } catch (parseError) {
            console.error('Error parsing response.json:', parseError);
            console.error('Content:', data);
            reject(parseError);
          }
        } catch (readError) {
          console.error(`Error reading response.json file: ${readError.message}`);
          reject(readError);
        }
      } else {
        // File doesn't exist yet, resolve with null
        resolve(null);
      }
    } catch (error) {
      console.error('Unexpected error checking for response file:', error);
      reject(error);
    }
  });
}

// Main function to process the user's query
async function processUserQuery(prompt) {
  console.log('Processing user query:', prompt);
  
  // Step 1: Delete the response file if it exists
  deleteResponseFileIfExists();
  
  // Step 2: Run the Python script with the prompt
  try {
    console.log('Starting Python script with prompt...');
    await runPythonScript(prompt);
    console.log('Python script started successfully');
  } catch (error) {
    console.error('Error running Python script:', error);
    return { followUp: 'Error running the Python script.', insights: 'Please try again later.', summary: '' };
  }
  
  // Step 3: Wait for the response file to be created
  console.log('Waiting for response.json file to be created...');
  let responseData = null;
  let attempts = 0;
  const maxAttempts = 30; // Wait up to 30 seconds (30 * 1000ms)
  
  while (attempts < maxAttempts && !responseData) {
    try {
      responseData = await checkForResponseFile();
      if (!responseData) {
        console.log(`Attempt ${attempts + 1}/${maxAttempts}: Response file not found yet, waiting...`);
        // Wait for 1 second before checking again
        await new Promise(resolve => setTimeout(resolve, 1000));
        attempts++;
      } else {
        console.log('Response file found!');
      }
    } catch (error) {
      console.error('Error reading response file:', error);
      return { followUp: 'Error reading the response file.', insights: 'Please try again later.', summary: '' };
    }
  }
  
  if (!responseData) {
    console.error(`Timeout after ${maxAttempts} attempts waiting for response.json file`);
    return { 
      followUp: 'Timeout waiting for response from the backend.', 
      insights: 'The system was unable to process your request in time. Please try again later.', 
      summary: '' 
    };
  }
  
  console.log('Successfully received response data from backend');
  return responseData;
}

// Function to get the latest data from the response file
function getLatestResponseData() {
  try {
    if (fs.existsSync(RESPONSE_FILE_PATH)) {
      console.log('Reading latest data from response.json file');
      const data = fs.readFileSync(RESPONSE_FILE_PATH, 'utf8');
      
      // Check if the file is empty or has invalid content
      if (!data || data.trim() === '') {
        console.warn('response.json file exists but is empty');
        return null;
      }
      
      try {
        const jsonData = JSON.parse(data);
        
        // Validate the structure of the response data
        if (!jsonData.followUp && !jsonData.insights) {
          console.warn('response.json is missing required fields (followUp or insights)');
        }
        
        return jsonData;
      } catch (parseError) {
        console.error('Error parsing response.json data:', parseError);
        console.error('Raw content:', data);
        return null;
      }
    }
    return null;
  } catch (error) {
    console.error('Error reading latest response data:', error);
    return null;
  }
}

module.exports = { processUserQuery, getLatestResponseData };

