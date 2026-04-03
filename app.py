import streamlit as st
import sqlite3
import pandas as pd
import hashlib

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect('admission.db', check_same_thread=False)
    c = conn.cursor()
    
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    ''')
    
    # Create admissions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS admissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            course TEXT,
            qualification TEXT,
            address TEXT
        )
    ''')
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

# --- Helper Functions ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def add_user(name, email, password):
    try:
        c.execute("INSERT INTO users(name, email, password) VALUES (?, ?, ?)", (name, email, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Email already exists

def login_user(email, password):
    c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    data = c.fetchall()
    return data

def add_admission(name, email, phone, course, qualification, address):
    try:
        c.execute('''
            INSERT INTO admissions(name, email, phone, course, qualification, address) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, email, phone, course, qualification, address))
        conn.commit()
        return True
    except Exception as e:
        return False

def view_all_admissions():
    c.execute("SELECT * FROM admissions")
    data = c.fetchall()
    return data

# --- Main App ---
def main():
    st.set_page_config(page_title="Admission Web App", page_icon="🎓", layout="wide")
    
    # Session State Initialization
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'user_email' not in st.session_state:
        st.session_state['user_email'] = None
    if 'is_admin' not in st.session_state:
        st.session_state['is_admin'] = False

    st.sidebar.title("Navigation")
    
    # Navigation logic based on login state
    if not st.session_state['logged_in']:
        menu = ["Home", "Login", "Signup"]
        choice = st.sidebar.selectbox("Menu", menu)
        
        if choice == "Home":
            st.title("🎓 Welcome to University Admission Portal")
            st.markdown("### Register for your future today!")
            
            # Main Banner Image
            st.image("https://images.unsplash.com/photo-1541339907198-e08756dedf3f?auto=format&fit=crop&w=1200&q=80", use_container_width=True)
            
            # Features Section
            st.markdown("---")
            st.subheader("Why Choose Us?")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.image("https://static.vecteezy.com/system/resources/previews/009/881/842/original/school-admission-open-banner-abstract-shape-free-vector.jpg", use_container_width=True)
                st.markdown("#### World-Class Facilities")
                st.write("Experience state-of-the-art laboratories, expansive libraries, and modern classrooms designed to foster innovation.")
                
            with col2:
                st.image("https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=600&q=80", use_container_width=True)
                st.markdown("#### Expert Faculty")
                st.write("Learn from industry leaders, distinguished researchers, and experienced professionals dedicated to academic excellence.")
                
            with col3:
                st.image("https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=600&q=80", use_container_width=True)
                st.markdown("#### Vibrant Campus Life")
                st.write("Join diverse student clubs, participate in global events, and build lifelong friendships in our community.")
                
            st.markdown("---")
            st.info("🎓 **Ready to join us?** Navigate to the **Login** or **Signup** page from the sidebar to begin your admission process.")
            
        elif choice == "Signup":
            st.subheader("Create New Student Account")
            new_name = st.text_input("Full Name")
            new_email = st.text_input("Email Address")
            new_password = st.text_input("Password", type='password')
            
            if st.button("Signup"):
                if new_name == "" or new_email == "" or new_password == "":
                    st.warning("Please make sure all fields are filled.")
                else:
                    hashed_pswd = make_hashes(new_password)
                    if add_user(new_name, new_email, hashed_pswd):
                        st.success("You have successfully created a valid Account")
                        st.info("Go to Login Menu to login")
                    else:
                        st.error("Email ID already exists. Please use a different email.")
                        
        elif choice == "Login":
            st.subheader("Login Section")
            email = st.text_input("Email")
            password = st.text_input("Password", type='password')
            
            if st.button("Login"):
                # Admin Authentication
                if email == "admin@example.com" and password == "admin123":
                    st.session_state['logged_in'] = True
                    st.session_state['user_email'] = email
                    st.session_state['is_admin'] = True
                    st.success("Logged in as Admin")
                    st.rerun()
                # User Authentication
                else:
                    hashed_pswd = make_hashes(password)
                    result = login_user(email, hashed_pswd)
                    if result:
                        st.session_state['logged_in'] = True
                        st.session_state['user_email'] = email
                        st.session_state['is_admin'] = False
                        st.success(f"Logged In as {email}")
                        st.rerun()
                    else:
                        st.warning("Incorrect Email/Password")

    else: # Logged In Context
        if st.session_state['is_admin']:
            menu = ["Dashboard", "Logout"]
        else:
            menu = ["Admission Form", "Logout"]
            
        choice = st.sidebar.selectbox("Menu", menu)
        
        if choice == "Admission Form":
            st.subheader("🎓 Student Admission Registration")
            st.write("Fill in the details to apply for admission.")
            
            with st.form("admission_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Full Name")
                    phone = st.text_input("Phone Number")
                    qualification = st.selectbox("Highest Qualification", ["High School", "Diploma", "Bachelors", "Masters"])
                with col2:
                    email = st.text_input("Email Address", value=st.session_state['user_email'], disabled=True)
                    course = st.selectbox("Desired Course", ["Computer Science", "Business Administration", "Engineering", "Arts", "Medicine"])
                    address = st.text_area("Home Address")
                    
                submit_button = st.form_submit_button(label="Submit Admission")
                
                if submit_button:
                    if name == "" or phone == "" or address == "":
                        st.warning("Please fill all the required fields.")
                    else:
                        if add_admission(name, email, phone, course, qualification, address):
                            st.success(f"Admission form submitted successfully for {name}!")
                            st.balloons()
                        else:
                            st.error("There was an error saving your details or you have already submitted an application.")

        elif choice == "Dashboard" and st.session_state['is_admin']:
            st.title("🛠️ Admin Dashboard")
            st.subheader("View all Admission Records")
            
            admissions_data = view_all_admissions()
            
            if admissions_data:
                # Create a DataFrame
                df = pd.DataFrame(admissions_data, columns=["ID", "Name", "Email", "Phone", "Course", "Qualification", "Address"])
                
                # Show Total Admissions
                st.metric("Total Admissions", len(df))
                
                # Display Interactive Table
                st.dataframe(df, use_container_width=True)
                
                # Download as CSV Option
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Data as CSV",
                    data=csv,
                    file_name='admissions_data.csv',
                    mime='text/csv',
                )
            else:
                st.info("No admission records found.")
                
        elif choice == "Logout":
            st.session_state['logged_in'] = False
            st.session_state['user_email'] = None
            st.session_state['is_admin'] = False
            st.success("Successfully logged out")
            st.rerun()

    # --- Footer ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #888; font-size: 14px;'>Developed the Web Application by <b>JoelX Orbit</b></div>", unsafe_allow_html=True)

if __name__ == '__main__':
    main()
