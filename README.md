# google-form-botter
This project is a Google Form automation tool that lets you simulate survey responses with custom probabilities. It’s useful for falsifying survey results.

# 📋 Google Form Auto-Responder

This project is a **Google Form automation tool** that simulates survey responses with custom probabilities. It’s designed for experimenting with Google Forms, testing survey logic, or learning how form submissions work behind the scenes.  

---

## 🚀 What it Does
- Converts a Google Form link into the hidden submission endpoint (`formResponse`).  
- Provides a helper snippet to extract the `entry.xxxxx` IDs of each question.  
- Lets you define:  
  - Number of questions  
  - Question IDs  
  - Answer options per question  
  - Percentage chance of each option being chosen  
- Randomly generates answers based on your probabilities.  
- Submits multiple responses automatically.  

---

## ✨ Features
- **Interactive setup** → prompts you step by step for questions and answers.  
- **Weighted randomization** → answer choices follow the probability distribution you set.  
- **Multiple submissions** → automatically generates as many responses as you want.  
- **Helper snippet** → reveals hidden question IDs inside the form.
- **Automated uploads** → automatically uploads the question responses into app 

---

## ⚠️ Limitations
- ❌ **Image uploads not supported**  
- ❌ **Checkbox (multi-select) questions not supported** (only single-option answers work)  
- ❌ **Works only on forms that allow multiple submissions** (cannot bypass Google’s “1 response only” setting)  
- ❌ **Does not work on forms requiring Google login**  

---

## 📖 Example Workflow

### Simply follow instructions after running main.py
- Paste the form link (From google form publishing)

### Define answer probabilities 
- Slider/Numerical option available to set probability (100% accuracy)

### Submit responses
- Select how many responses you would like

⚠️ Disclaimer

This project is for educational and testing purposes only.
Do not use it to tamper with or spam real surveys — this may violate Google’s Terms of Service.
