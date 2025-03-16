# AI-Powered Email Assistant

## 📧 Overview
The **AI-Powered Email Assistant** is an intelligent web application that streamlines email management using **Gmail API** and **LangChain**. This assistant can:

- Categorize incoming emails (Work, Personal, Promotional, Spam)
- Analyze urgency levels (Urgent, High, Medium, Low)
- Summarize email content
- Generate professional email drafts and save them in your **Gmail** drafts folder

The assistant uses **GROQ LLM (mixtral-8x7b-32768)** for AI-based email processing and **Streamlit** for an intuitive user interface.

## 🛠️ Features

- **Email Categorization**: Automatically classifies emails into Work, Personal, Promotional, or Spam.
- **Urgency Detection**: Evaluates the urgency of emails to prioritize important messages.
- **Email Summarization**: Generates concise summaries of email content.
- **Draft Creation**: Produces professional email responses and saves them as drafts in Gmail.
- **User Interface**: Interactive dashboard using **Streamlit** for better email navigation and response management.

## 🚀 Setup Instructions

### 1. Prerequisites
Ensure you have the following installed:

- Python 3.10+
- Google Cloud account with Gmail API enabled

### 2. Enable Gmail API and Download Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. **Create a New Project**:
    - Click [here](https://console.cloud.google.com/projectcreate).
    - Provide a project name and click **Create**.
3. **Enable Gmail API**:
    - Navigate to **APIs & Services** > **Library**.
    - Search for **Gmail API** and click **Enable**.
4. **Create Credentials**:
    - Go to **APIs & Services** > **Credentials**.
    - Click **Create Credentials** > **OAuth 2.0 Client ID**.
    - Set up **User Type** as **External** (if required) and follow the setup.
    - Choose **Desktop Application** and set the scope to `https://mail.google.com/`.
5. **Download Credentials**:
    - Download the generated `credentials.json` file and place it in the project folder.
**Alternative Setup (Google Quickstart Guide)**

Alternatively, you can follow the official [Google Gmail API Quickstart Guide](https://developers.google.com/gmail/api/quickstart/python#authorize_credentials_for_a_desktop_application) for a detailed step-by-step guide to enable and authorize the Gmail API for a desktop application

### 3. Clone the Repository

```bash
$ git clone <repository_url>
$ cd ai-email-assistant
```

### 4. Create and Activate a Virtual Environment

Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```
Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Set Environment Variables

Create a `.env` file in the project root and add the following:

```
GROQ_API_KEY=your_groq_api_key
```

Ensure your Google API credentials are in the same folder as `credentials.json`.

### 7. Authenticate with Gmail

1. Run the application.
2. Follow the instructions to authenticate your Google account and save the `token.json`.

### 8. Run the Application

```bash
streamlit run app.py
```

## 📊 Usage

1. **Authenticate Gmail**: Upload your `credentials.json` and follow the authentication flow.
2. **Process Emails**: Click on **Process New Emails** to fetch and analyze recent emails.
3. **View Categorized Emails**: Explore emails categorized by Work, Personal, Promotional, or Spam.
4. **Generate Drafts**: Click **Generate Draft Reply** to create and save a professional draft in your Gmail account.

## Features in Detail

### Email Processing
- Fetches and analyzes unread emails from Gmail
- Categorizes emails into Work, Personal, Promotional, or Spam
- Determines urgency levels (Urgent, High, Medium, Low)
- Generates concise summaries of email content

### Draft Generation
- Creates AI-powered draft replies
- Maintains appropriate tone based on email category
- Includes proper greeting and closing
- Professional formatting

### User Interface
- Clean and intuitive dashboard
- Email statistics and analytics
- Category-based filtering
- Customizable processing settings

## 📂 Project Structure

```
├── app.py                 # Main Streamlit app
├── email_processor.py     # Core email processing logic
├── gmail_auth.py          # Gmail API authentication
├── requirements.txt       # Project dependencies
├── token.json             # OAuth token (generated during auth)              
├── .env                   # Environment variables
├── credentials.json       # Gmail API credentials (not included)
└── README.md              # Documentation
```

## 📌 Dependencies

All necessary packages are listed in `requirements.txt`:

```
streamlit
langchain-groq
langchain-google-community
python-dotenv
```

Install them via:

```bash
pip install -r requirements.txt
```
## 🎯 Known Limitations

- Email processing is limited to recent unread emails
- Draft generation may take a few seconds per email
- Rate limiting may apply for large numbers of emails
- Currently supports English language emails only
  
## 🧐 Troubleshooting

1. **Gmail Authentication Issues**:
   - Ensure `credentials.json` and `token.json` are correctly placed.
   - Re-authenticate if the token expires.

2. **Missing API Key**:
   - Ensure `GROQ_API_KEY` is set in `.env`.

3. **Permission Errors**:
   - Ensure the Gmail API is enabled and the OAuth scope is correct.

## 📧 Contribution

Contributions are welcome! Feel free to open an issue or submit a pull request.

## 📜 License

MIT License.

