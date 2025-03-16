from langchain_community.tools.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)
import streamlit as st
import os
import webbrowser
from google_auth_oauthlib.flow import Flow

def initialize_gmail():
    """Initialize Gmail credentials and API resource."""
    try:
        if not os.path.exists("credentials.json"):
            st.error("credentials.json file not found. Please upload your Google API credentials.")
            uploaded_file = st.file_uploader("Upload credentials.json", type="json")
            if uploaded_file:
                with open("credentials.json", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success("Credentials uploaded successfully!")
                st.rerun()
            return None, None

        if not os.path.exists("token.json"):
            st.warning("Gmail authentication required.")
            # Create the flow using the client secrets file
            flow = Flow.from_client_secrets_file(
                'credentials.json',
                scopes=['https://mail.google.com/'],
                redirect_uri='urn:ietf:wg:oauth:2.0:oob'
            )

            auth_url, _ = flow.authorization_url(prompt='consent')

            st.markdown(f"""
            ### Gmail Authentication Required
            1. Click the link below to authorize the application:
            2. [Click here to authenticate with Gmail]({auth_url})
            3. Copy the authorization code and paste it below:
            """)

            auth_code = st.text_input("Enter the authorization code:")
            if auth_code:
                flow.fetch_token(code=auth_code)
                with open("token.json", "w") as token_file:
                    credentials = flow.credentials
                    import json
                    token_file.write(json.dumps({
                        'token': credentials.token,
                        'refresh_token': credentials.refresh_token,
                        'token_uri': credentials.token_uri,
                        'client_id': credentials.client_id,
                        'client_secret': credentials.client_secret,
                        'scopes': credentials.scopes
                    }))
                st.success("Authentication successful!")
                st.rerun()
            return None, None

        credentials = get_gmail_credentials(
            token_file="token.json",
            scopes=["https://mail.google.com/"],
            client_secrets_file="credentials.json",
        )
        api_resource = build_resource_service(credentials=credentials)
        return credentials, api_resource
    except Exception as e:
        st.error(f"Error initializing Gmail: {str(e)}")
        if "token.json" in str(e):
            if os.path.exists("token.json"):
                os.remove("token.json")
            st.warning("Authentication token expired. Please authenticate again.")
            st.rerun()
        return None, None