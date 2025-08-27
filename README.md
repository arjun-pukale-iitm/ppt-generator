# PPTX Builder

Turn your text or markdown into a fully formatted PowerPoint presentation using a custom template.

## **Setup Instructions**

### **1. Clone the Repository**
```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

### **2. Install Dependencies**
Make sure you have Python 3.9+ installed. Then:
```bash
pip install -r requirements.txt
```

### **3. Start the FastAPI Server**
```bash
uvicorn main:app
```

### **4. Access the Web Interface**
Open your browser and go to:
```
http://127.0.0.1:8000/static
```

### **5. Generate a Presentation**
1. Paste your text/markdown in the textbox.  
2. Optionally add tone/guidance (e.g., “Investor pitch deck”).  
3. Select your LLM provider and enter your API key.  
4. Upload your PPTX/POTX template.  
5. Click **Generate Presentation**.  

Your customized presentation will be generated and ready to download.