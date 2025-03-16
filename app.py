import streamlit as st
import os
from gmail_auth import initialize_gmail
from email_processor import EmailProcessor
from datetime import datetime, timedelta
import hashlib
import html

# Page configuration
st.set_page_config(
    page_title="Email AI Agent",
    page_icon="📧",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
        background-color: #f8f9fa;
    }
    .stButton > button {
        width: 100%;
        background-color: #0066cc;
        color: white;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        border: none;
        font-weight: 500;
    }
    .email-card {
        background-color: white;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .email-content {
        flex: 1;
    }
    .email-sender {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    .email-subject {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
    .email-summary {
        color: #444;
        margin-bottom: 1rem;
    }
    .priority-tag {
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 500;
        display: inline-block;
    }
    .priority-urgent {
        background-color: #fecaca;
        color: #dc2626;
        background-color: #dc2626; /* Red background */
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 500;
        display: inline-block;
    }
    .priority-high {
        background-color: #fee2e2;
        color: #dc2626;
    }
    .priority-medium {
        background-color: #fef9c3;
        color: #854d0e;
    }
    .priority-low {
        background-color: #dcfce7;
        color: #16a34a;
    }
    .stats-container {
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    .stats-card {
        flex: 1;
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stats-number {
        font-size: 2rem;
        font-weight: 600;
        color: #0066cc;
        margin-bottom: 0.5rem;
    }
    .stats-label {
        color: #666;
        font-size: 0.9rem;
    }
    .action-buttons {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    .action-button {
        padding: 4px 12px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.9rem;
        border: 1px solid #e5e7eb;
        background: white;
    }
    .action-button:hover {
        background: #f3f4f6;
    }
    .generate-reply-button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 5px 10px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.9rem;
    }
    .generate-reply-button:hover {
        background-color: #45a049;
    }
    </style>
""", unsafe_allow_html=True)

def safe_html(text):
    """Safely escape text for HTML display."""
    return html.escape(str(text)) if text else ""

def format_time_ago(timestamp):
    """Format timestamp as relative time."""
    if not timestamp:
        return "Never"
    now = datetime.now()
    diff = now - timestamp
    if diff.seconds < 60:
        return "Just now"
    elif diff.seconds < 3600:
        return f"{diff.seconds // 60} minutes ago"
    else:
        return f"{diff.seconds // 3600} hours ago"

def generate_draft_reply(processor, email):
    """Generate a draft reply for the selected email."""
    with st.spinner('Generating draft reply...'):
        success, message = processor.generate_draft_reply(email)
        if success:
            st.success(message)
        else:
            st.error(message)

def main():
    if 'processed_emails' not in st.session_state:
        st.session_state.processed_emails = []
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = None
    if 'selected_email' not in st.session_state:
        st.session_state.selected_email = None  # Track the selected email for draft generation

    st.title("📧 Email AI Agent")
    st.markdown("Smart email management powered by AI")

    # Initialize Gmail
    credentials, api_resource = initialize_gmail()
    if not credentials or not api_resource:
        st.warning("Please complete Gmail authentication to continue.")
        return

    # Sidebar configuration
    with st.sidebar:
        st.header("Settings")
        search_period = st.selectbox(
            "Time Range",
            ["1d", "2d", "3d", "7d"],
            index=1,
            format_func=lambda x: {
                "1d": "Last 24 hours",
                "2d": "Last 2 days",
                "3d": "Last 3 days",
                "7d": "Last week"
            }[x]
        )

        max_results = st.slider(
            "Number of Emails",
            min_value=5,
            max_value=50,
            value=10,
            step=5
        )

        query_base = st.text_input(
            "Filter Query",
            value="category:primary"
        )

    # Process emails button
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("🔄 Process New Emails", use_container_width=True):
            processor = EmailProcessor(api_resource)
            query = f"is:unread newer_than:{search_period} {query_base}"
            with st.spinner("Processing emails..."):
                st.session_state.processed_emails = processor.process_emails(
                    query=query,
                    max_results=max_results
                )
                st.session_state.last_refresh = datetime.now()

    with col2:
        st.caption(f"Last updated: {format_time_ago(st.session_state.last_refresh)}")

    # Display results
    if st.session_state.processed_emails:
        emails = st.session_state.processed_emails

        # Calculate statistics
        categories = {
            'Work': 0,
            'Personal': 0,
            'Promotional': 0,
            'Spam': 0
        }

        for email in emails:
            categories[email['category']] = categories.get(email['category'], 0) + 1

        # Display statistics
        st.markdown("### Email Overview")

        # Create columns based on the number of stats_data items
        stats_data = [("Total", len(emails))] + list(categories.items())
        cols = st.columns(len(stats_data))

        for i, (label, count) in enumerate(stats_data):
            with cols[i]:
                st.markdown(f"""
                <div class="stats-card">
                    <div class="stats-number">{count}</div>
                    <div class="stats-label">{label} Emails</div>
                </div>
                """, unsafe_allow_html=True)

        # Email tabs
        tabs = st.tabs(["📥 All", "💼 Work", "👤 Personal", "🏷️ Promotional", "⚠️ Spam"])

        # Function to generate a unique key for an email
        def generate_unique_key(email):
            # Combine email metadata to create a unique string
            unique_string = f"{email['subject']}_{email['sender']}"
            # Hash the string to create a unique key
            return hashlib.md5(unique_string.encode()).hexdigest()

        def display_emails(filtered_emails):
            if not filtered_emails:
                st.info("No emails in this category.")
                return

            for index, email in enumerate(filtered_emails):
                urgency = email['urgency'].split(":")[0].strip().lower()  # Extracts "urgent"
                priority_class = f"priority-{email['urgency'].lower()}"
                # Apply urgent class if email is urgent
                urgent_class = "urgent" if urgency == "urgent" else ""

                email_html = f"""
                <div class="email-card">
                    <div class="email-content">
                        <div class="email-sender">{safe_html(email['sender'])}</div>
                        <div class="email-subject">{safe_html(email['subject'])}</div>
                        <div class="email-summary">{safe_html(email['summary'])}</div>
                        <div class="email-meta">
                            <span>Category: {safe_html(email['category'])}</span>
                            <span class="priority-tag {priority_class}">
                                {safe_html(email['urgency'])}
                            </span>
                        </div>
                    </div>
                </div>
                """
                st.markdown(email_html, unsafe_allow_html=True)

                
                # Generate a unique key for the button
                unique_key = generate_unique_key(email)
                if st.button(f"✍️ Generate Draft Reply for: {email['subject']}", key=unique_key):
                    st.session_state.selected_email = email  # Store the selected email in session state
                    st.rerun()  # Rerun the app to trigger the draft generation logic

        # Display emails in tabs
        with tabs[0]:
            display_emails(emails)

        with tabs[1]:
            display_emails([e for e in emails if e['category'] == 'Work'])

        with tabs[2]:
            display_emails([e for e in emails if e['category'] == 'Personal'])

        with tabs[3]:
            display_emails([e for e in emails if e['category'] == 'Promotional'])

        with tabs[4]:
            display_emails([e for e in emails if e['category'] == 'Spam'])

        # Draft generation logic
        if st.session_state.selected_email:
            st.markdown("### Draft Reply")
            selected_email = st.session_state.selected_email
            processor = EmailProcessor(api_resource)
            success, message = processor.generate_draft_reply(selected_email)
            if success:
                st.success("Draft created successfully!")
            else:
                st.error(f"Error: {message}")

    else:
        st.info("👋 Welcome! Click 'Process New Emails' to start analyzing your inbox.")

if __name__ == "__main__":
    main()