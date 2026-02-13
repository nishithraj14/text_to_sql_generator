import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from urllib.parse import quote_plus
from langchain_core.prompts import ChatPromptTemplate
import pymysql
import ast
import sqlparse
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === Streamlit UI ===
st.title("🧠 Text_to_SQL")
st.subheader("This application can connect to all tables in the selected database and generate required queries")

# Database selection
db_options = ['enterprise_saas', 'e_commerce', 'analytics']
selected_db = st.selectbox("Choose a database schema", db_options)

# NL query input
user_question = st.text_input("Enter your natural language query")

# --- Configuration - Read from Environment Variables ---
host = os.getenv('MYSQL_HOST', '127.0.0.1')
port = os.getenv('MYSQL_PORT', '3306')
username = os.getenv('MYSQL_USER', 'root')
password = os.getenv('MYSQL_PASSWORD', '')
groq_api_key = os.getenv('GROQ_API_KEY', '')

# Validate required environment variables
if not password:
    st.error("❌ MYSQL_PASSWORD not found in environment variables")
    st.info("💡 Create a .env file with your MySQL password")
    st.code("""
# Create a .env file in your project root with:
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password_here
GROQ_API_KEY=your_groq_api_key_here
    """)
    st.stop()

if not groq_api_key:
    st.error("❌ GROQ_API_KEY not found in environment variables")
    st.info("💡 Add GROQ_API_KEY to your .env file")
    st.stop()

encoded_password = quote_plus(password)

# --- LangChain SQL Setup ---
@st.cache_resource
def get_database_connection(database_name):
    """Cache database connection to avoid recreating it on every interaction"""
    mysql_uri = f"mysql+pymysql://{username}:{encoded_password}@{host}:{port}/{database_name}"
    return SQLDatabase.from_uri(mysql_uri, sample_rows_in_table_info=3)

try:
    db = get_database_connection(selected_db)
    st.success(f"✅ Connected to database: {selected_db}")
except Exception as e:
    st.error(f"❌ Failed to connect to database: {e}")
    st.info("💡 Check your .env file and make sure MySQL is running")
    st.stop()

def get_schema(db):
    """Get table schema information"""
    return db.get_table_info()

# Prompt template
template = """Based on the table schema below, write a SQL query that would answer the user's question:

IMPORTANT RULES:
- Only provide the SQL query, nothing else
- Provide the SQL query in a single line without line breaks
- Use proper MySQL syntax
- Do not include any explanations or markdown formatting
- Do not include semicolon at the end

Table Schema:
{schema}

Question: {question}

SQL Query:"""

prompt = ChatPromptTemplate.from_template(template)

# LLM setup
@st.cache_resource
def get_llm():
    """Cache LLM instance"""
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=groq_api_key,
        temperature=0
    )

llm = get_llm()

# Create SQL chain
sql_chain = (
    RunnablePassthrough.assign(schema=lambda _: get_schema(db))
    | prompt
    | llm.bind(stop=["\nSQLResult:", "\n\n"])
    | StrOutputParser()
)

# === Button to trigger query ===
if st.button("🔍 Generate SQL and Run", type="primary"):
    if not user_question.strip():
        st.warning("⚠️ Please enter a natural language query.")
    else:
        with st.spinner("🤖 Generating SQL query..."):
            try:
                # Step 1: Generate SQL query
                sql_query = sql_chain.invoke({"question": user_question})
                
                # Clean the SQL query
                sql_query = sql_query.strip()
                prefixes_to_remove = ['```sql', '```', 'SQL Query:', 'Query:']
                for prefix in prefixes_to_remove:
                    if sql_query.startswith(prefix):
                        sql_query = sql_query[len(prefix):].strip()
                
                sql_query = sql_query.rstrip(';').strip('`').strip()
                formatted_sql = sqlparse.format(sql_query, reindent=True, keyword_case='upper')
                
                st.subheader("📝 Generated SQL Query:")
                st.code(formatted_sql, language="sql")

                # Step 2: Run SQL and display result
                with st.spinner("⚡ Executing query..."):
                    result = db.run(sql_query)
                    
                    st.subheader("📊 Query Results:")
                    
                    if isinstance(result, str):
                        try:
                            parsed_result = ast.literal_eval(result)
                            
                            if isinstance(parsed_result, list):
                                if len(parsed_result) == 0:
                                    st.info("No results found.")
                                elif isinstance(parsed_result[0], tuple):
                                    df = pd.DataFrame(parsed_result)
                                    st.dataframe(df, use_container_width=True)
                                else:
                                    st.write(parsed_result)
                            else:
                                st.write(parsed_result)
                        except:
                            st.text(result)
                    else:
                        st.write(result)
                
                st.success("✅ Query executed successfully!")

            except pymysql.err.ProgrammingError as e:
                st.error(f"❌ SQL Syntax Error: {e}")
                st.info("💡 The generated SQL query has syntax errors. Try rephrasing your question.")
                
            except pymysql.err.OperationalError as e:
                st.error(f"❌ Database Error: {e}")
                st.info("💡 Make sure tables exist in the database.")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Try rephrasing your question or check if the database has tables.")

# Sidebar with information
with st.sidebar:
    st.header("ℹ️ Information")
    st.write("**How to use:**")
    st.write("1. Select a database schema")
    st.write("2. Enter your question in plain English")
    st.write("3. Click 'Generate SQL and Run'")
    
    st.write("---")
    st.write("**Example queries:**")
    st.code("How many customers are in the database?", language="text")
    st.code("What is the total revenue?", language="text")
    st.code("Show top 5 products by sales", language="text")
    
    st.write("---")
    st.write("**Database Info:**")
    try:
        tables = db.get_usable_table_names()
        if tables:
            st.write(f"📋 Available tables: {len(tables)}")
            with st.expander("View table names"):
                for table in tables:
                    st.write(f"• {table}")
        else:
            st.warning("⚠️ No tables found in this database")
            st.info("You need to import data into the database first")
    except:
        st.write("Connect to a database to see tables")