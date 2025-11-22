# CS5351 Project Metrics Tool  
An enhanced tool for generating agile metrics and burn-down charts from GitHub issues. - For CS5351 Project  

# Project Setup Guide  

This project consists of a **Flask backend** and a **Vue 3 frontend**. Before running, please ensure that [Python 3.x](https://www.python.org/downloads/) and [Node.js](https://nodejs.org/) are installed on your system.  

## 1️⃣ Launching the Backend  

1. Create a virtual environment:  
```powershell
python -m venv venv
```
2. Activate the virtual environment:  
```powershell
.\venv\Scripts\Activate.ps1
```
3. Install required Python dependencies:  
```powershell
pip install -r requirements.txt
```
4. Start the Flask backend server:  
```powershell
python app.py
```
If the following output appears, the backend has started successfully:
```
🌐 Flask backend running at http://127.0.0.1:5000
* Serving Flask app 'app'
* Debug mode: on
```
> ⚠️ Note: Keep this terminal open as the frontend depends on the backend API.  

## 2️⃣ Launching the Frontend  

1. Open a new terminal (do **not** close the backend terminal) and navigate to the frontend directory:  
```powershell
cd frontend
```
2. Install frontend dependencies:  
```bash
npm install
```
3. Start the frontend development server:  
```bash
npm run dev
```
After successful startup, you should see output similar to:  
```
> my-vue-app@0.0.0 dev  
> vite
  VITE v7.1.6  ready in 9078 ms
  ➜  Local:   http://localhost:5174/   (Port may vary)
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```
4. Open your browser and navigate to the **Local** URL to access the frontend application.  

✅ Recommended Startup Sequence:   
1. Activate backend virtual environment and start Flask server    
2. Navigate to frontend, install dependencies, and run development server    
3. Access the frontend via browser  
