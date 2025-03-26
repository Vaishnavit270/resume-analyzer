import pandas as pd
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "vaishnavit22hcompe@student.mes.ac.in"  # Change this
EMAIL_PASSWORD = "elfc tfvx abuf vdzp"  # Change this

def send_email(to_email, candidate_name, job_title, company_name):
    """ Sends an email to the selected candidate with company details. """
    if pd.isna(to_email) or not to_email.strip():
        st.warning(f"Skipping {candidate_name} due to missing email.")
        return False

    to_email = str(to_email).strip()  # Ensure email is a string

    subject = f"Job Selection Notification from {company_name}"
    body = f"""Dear {candidate_name},

Congratulations! You have been selected for the {job_title} position at {company_name}.

We are excited to have you join our team and will be in touch soon with further details.

Best regards,  
HR Team  
{company_name}
"""

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error sending email to {candidate_name} ({to_email}): {e}")
        return False

def filter_candidates(df, job_requirements):
    """ Filters candidates based on job field matching and removes invalid emails. """
    if "Predicted Field" not in df.columns:
        st.error("CSV file is missing the required 'Predicted Field' column.")
        return pd.DataFrame()

    filtered_df = df[df['Predicted Field'].astype(str).str.contains(job_requirements, case=False, na=False)]

    # Ensure 'Mail' column exists and remove rows where it's empty or NaN
    if "Mail" in filtered_df.columns:
        filtered_df = filtered_df.dropna(subset=['Mail'])  # Remove rows where Mail is NaN
        filtered_df = filtered_df[filtered_df['Mail'].astype(str).str.strip() != ""]  # Remove empty emails

    return filtered_df

def main():
    st.title("Candidate Selection System")
    
    company_name = st.text_input("Enter Your Company Name")
    if not company_name.strip():
        st.warning("Please enter your company name before proceeding.")
    
    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
    job_requirements = st.text_input("Enter Job Requirements (e.g., Data Science, Marketing)")
    
    if uploaded_file and job_requirements and company_name.strip():
        df = pd.read_csv(uploaded_file)

        if "Name" not in df.columns or "Mail" not in df.columns:
            st.error("CSV file must contain 'Name' and 'Mail' columns.")
            return

        filtered_candidates = filter_candidates(df, job_requirements)
        
        st.write("### Filtered Candidates")
        st.dataframe(filtered_candidates)
        
        selected_candidates = st.multiselect("Select Candidates to Notify", filtered_candidates['Name'].tolist())
        
        if st.button("Notify Selected Candidates"):
            for candidate in selected_candidates:
                candidate_row = filtered_candidates[filtered_candidates['Name'] == candidate].iloc[0]
                email = candidate_row['Mail']

                if send_email(email, candidate, job_requirements, company_name):
                    st.success(f"Email sent to {candidate} ({email})")
                else:
                    st.error(f"Failed to send email to {candidate}")
    
if __name__ == "__main__":
    main()
