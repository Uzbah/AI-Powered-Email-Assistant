from langchain_community.agent_toolkits import GmailToolkit
from langchain_google_community.gmail.utils import clean_email_body
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_community.gmail.search import SearchArgsSchema, Resource
from email.header import decode_header
import streamlit as st
import time
import os
from dotenv import load_dotenv

load_dotenv()


class EmailProcessor:

    def __init__(self, api_resource):
        """Initialize the EmailProcessor with necessary components."""
        self.toolkit = GmailToolkit(api_resource=api_resource)
        self.tools = self.toolkit.get_tools()
        self.search_tool = next(
            (tool for tool in self.tools if tool.name == "search_gmail"), None)
        self.draft_tool = next(
            (tool for tool in self.tools if tool.name == "create_gmail_draft"), None)

        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ API key not found")

        self.groq_llm = ChatGroq(
            model="mixtral-8x7b-32768",
            temperature=0.7,
            max_tokens=500,  # Increased for draft generation
            api_key=groq_api_key)

        self._initialize_chains()

    def _initialize_chains(self):
        """Initialize the processing chains."""
        self.categorization_chain = self._create_categorization_chain()
        self.urgency_chain = self._create_urgency_chain()
        self.summarization_chain = self._create_summarization_chain()
        self.draft_chain = self._create_draft_chain()

    def _create_categorization_chain(self):
        prompt = ChatPromptTemplate.from_messages([(
            "system",
            """You are a helpful assistant that categorizes emails into one of these types: Work, Personal, Promotional, or Spam. 
         Your response must be exactly one of these four words: Work, Personal, Promotional, or Spam. 
         Do not include any explanations, notes, or additional text."""
        ), ("human", "{email_content}")])
        return prompt | self.groq_llm

    def _create_urgency_chain(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             """Rate the email's urgency using exactly one of these levels:
                - Urgent: Immediate action required (deadlines, emergencies)
                - High: Important but not immediate
                - Medium: Normal priority
                - Low: Can wait

                Respond with only the urgency level.
                Respond with only the urgency level in the format:
                [URGENCY_LEVEL]"""),
            ("human", "{email_content}")
        ])
        return prompt | self.groq_llm

    def _create_summarization_chain(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             """Create a one-line summary of the email's core message.
                Focus on actionable content or key information.
                Ignore technical elements, images, or formatting.
                Be concise and direct."""), ("human", "{email_content}")
        ])
        return prompt | self.groq_llm

    def _create_draft_chain(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             """You are an AI assistant helping to draft email replies.
                Create a professional and courteous response based on the original email.
                Keep the tone appropriate for the email category (formal for work, friendly for personal).
                Be concise but complete.
                Include:
                - Appropriate greeting
                - Clear response to the main points
                - Professional closing
                - Your signature line

                Format the response appropriately with line breaks."""),
            ("human", """Original Email Content: {email_content}
            Category: {category}
            Urgency: {urgency}""")
        ])
        return prompt | self.groq_llm

    def generate_draft_reply(self, email):
        """Generate and save a draft reply to an email."""
        try:
            if not self.draft_tool:
                raise ValueError("Draft tool not initialized")

            # Generate draft content
            draft_response = self.draft_chain.invoke({
                "email_content":
                email['body'],
                "category":
                email['category'],
                "urgency":
                email['urgency']
            }).content

            # Create draft in Gmail
            draft_args = {
                "message": {
                    "to": email['sender'],
                    "subject": f"Re: {email['subject']}",
                    "body": draft_response
                }
            }

            self.draft_tool.run(draft_args)
            return True, "Draft created successfully"

        except Exception as e:
            return False, f"Error creating draft: {str(e)}"

    def decode_email_subject(self, subject):
        """Decode email subject."""
        try:
            decoded_parts = decode_header(subject)
            decoded_subject = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded_subject += part.decode(encoding or "utf-8",
                                                   errors="replace")
                else:
                    decoded_subject += part
            return decoded_subject
        except Exception:
            return subject

    def process_emails(self,
                       query="is:unread newer_than:2d category:primary",
                       max_results=5):
        """Process emails with improved error handling and consistent output."""
        if not self.search_tool:
            return []

        try:
            search_args = SearchArgsSchema(query=query,
                                           resource=Resource.MESSAGES,
                                           max_results=max_results)

            with st.spinner('Processing emails...'):
                results = self.search_tool.run(search_args.model_dump())
                processed_emails = []

                total_emails = len(results)
                for idx, result in enumerate(results, 1):
                    try:
                        # Clean and prepare email content
                        cleaned_body = clean_email_body(result['body'])
                        decoded_subject = self.decode_email_subject(
                            result['subject'])
                        truncated_body = cleaned_body[:
                                                      2000]  # Limit content length for processing

                        # Process email components
                        category = self.categorization_chain.invoke({
                            "email_content":
                            truncated_body
                        }).content.strip().capitalize()

                        # Validate category
                        valid_categories = ["Work", "Personal", "Promotional", "Spam"]
                        if category not in valid_categories:
                            category = "Spam"  # Default to Spam if the category is invalid

                        urgency = self.urgency_chain.invoke({
                            "email_content":
                            truncated_body
                        }).content.strip()

                        summary = self.summarization_chain.invoke({
                            "email_content":
                            truncated_body
                        }).content.strip()

                        processed_emails.append({
                            'subject': decoded_subject,
                            'sender': result['sender'],
                            'category': category,
                            'urgency': urgency,
                            'summary': summary,
                            'body': cleaned_body
                        })

                    except Exception as e:
                        st.error(f"Error processing email: {str(e)}")
                        continue

                    time.sleep(0.2)  # Small delay to prevent rate limiting

                return processed_emails

        except Exception as e:
            st.error(f"Error fetching emails: {str(e)}")
            return []
