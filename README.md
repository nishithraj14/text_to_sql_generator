# 🧠 Text-to-SQL Generator

Convert natural language queries into SQL and execute them on MySQL databases using AI.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-latest-red)
![LangChain](https://img.shields.io/badge/LangChain-latest-green)

![text_to_sqlsrec](https://github.com/user-attachments/assets/f4dc7cd0-f4f1-41ab-82fc-019982e9367e)



## 🚀 Features

- 🤖 AI-powered natural language to SQL conversion
- 💬 Simple conversational interface
- 🗄️ Multi-database support (Enterprise SaaS, E-Commerce, Analytics)
- 📊 Interactive result display
- ⚡ Real-time query execution

## 📋 Prerequisites

- Python 3.11+
- MySQL Server 9.6+ (or 8.0+)
- Groq API Key ([Get one here](https://console.groq.com/))

## 🛠️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/nishithraj14/text_to_sql_generator.git
cd text_to_sql_generator
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up MySQL Database

Create databases:
```sql
CREATE DATABASE enterprise_saas;
CREATE DATABASE e_commerce;
CREATE DATABASE analytics;
```

Run the setup script:
```bash
mysql -u root -p < database/setup.sql
```

### 4. Configure Environment Variables

Copy the example file:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password

GROQ_API_KEY=your_groq_api_key
```

### 5. Run the application
```bash
streamlit run main.py
```

## 💡 Example Queries

### Enterprise SaaS
- "How many companies are there?"
- "What is the total MRR from all subscriptions?"
- "Show all active Enterprise subscriptions"

### E-Commerce
- "What is the total revenue from all orders?"
- "Show top 5 most expensive products"
- "List all customers from USA"

### Analytics
- "What is the total campaign budget?"
- "Show conversion revenue by campaign"
- "Which page has the most visits?"

## 🏗️ Tech Stack

- **Frontend**: Streamlit
- **LLM**: Groq (LLaMA 3.3 70B)
- **Framework**: LangChain
- **Database**: MySQL
- **Language**: Python 3.11

## 📁 Project Structure
```
text-to-sql/
├── main.py                    # Local development
├── streamlit_deploy.py        # Deployment version
├── requirements.txt           # Dependencies
├── .env.example              # Environment template
├── README.md                # Documentation
├── SECRETS_FORMAT.txt       # Deployment secrets template
├── DEPLOYMENT_GUIDE.md      # Deployment guide
└── database/
    └── setup.sql           # Database setup
```

## 🚀 Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for Streamlit Cloud deployment instructions.

## 📝 License

MIT License

## ⚠️ Security

Never commit `.env` or files with API keys/passwords to Git.
