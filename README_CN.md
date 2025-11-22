# CS5351-project-metrics-tool  
A enhanced tool for generating agile metrics and burn-down charts from GitHub issues. - For CS5351 Project  

# 项目启动指南  

本项目包含 **Flask 后端** 与 **Vue 3 前端**，运行前需确保已安装 [Python 3.x](https://www.python.org/downloads/) 和 [Node.js](https://nodejs.org/)。  

## 1️⃣ 启动后端  

1. 创建虚拟环境：  

```powershell
python -m venv venv
```

2. 激活虚拟环境：  
```powershell
.\venv\Scripts\Activate.ps1
```
3.安装依赖   
```powershell
pip install -r requirements.txt
```

4.启动 Flask 后端：  
```powershell
python app.py
```
 
如果出现以下信息，表示后端已成功启动：  
```
🌐 Flask backend running at http://127.0.0.1:5000
* Serving Flask app 'app'
* Debug mode: on
```


2️⃣ 启动前端    
1.打开新终端，切换到前端目录（请不要关闭之前的后端终端）：    
```powershell
cd frontend
```

2.安装前端依赖：  
```bash
npm install
```

3.启动前端开发服务器：  
```bash
npm run dev
```


启动成功后会显示类似信息：  
```
> my-vue-app@0.0.0 dev
> vite
  VITE v7.1.6  ready in 9078 ms
  ➜  Local:   http://localhost:5174/   (Port may vary)
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

4.打开浏览器访问 Local 地址即可查看前端页面。      

✅ 推荐启动顺序：  

1. 激活后端虚拟环境并启动 Flask 服务器  

2. 导航至前端，安装依赖项并运行开发服务器  

3. 通过浏览器访问前端  
