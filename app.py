import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import plotly.express as px
import sqlite3
from hashlib import sha256

# Database setup
conn = sqlite3.connect('user.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS detail
             (username TEXT PRIMARY KEY, password TEXT)''')
conn.commit()

def create_hashed_password(password):
    return sha256(password.encode()).hexdigest()

def register():
    st.title('Register')

    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    
    if len(password) < 8:
        st.warning('Password should be at least 8 characters long')
        return

    hashed_pwd = create_hashed_password(password)

    register_button = st.button('Register')

    if register_button:
        try:
            c.execute("INSERT INTO detail (username, password) VALUES (?, ?)", (username, hashed_pwd))
            conn.commit()
            st.success("Registered Successfully. Please go to Login.")
        except sqlite3.IntegrityError:
            st.warning("This username is already registered. Please choose a different one.")

def login():
    st.title('Login')
    st.write('Register before Login.')

    username = st.text_input('Username', key="login_username")
    password = st.text_input('Password', type='password', key="login_password")
    hashed_pwd = create_hashed_password(password)

    login_button = st.button('Login')

    if login_button:
        c.execute("SELECT * FROM detail WHERE username = ? AND password = ?", (username, hashed_pwd))
        data = c.fetchone()
        if data:
            st.session_state.logged_in = True
            return True
            st.empty()  # Clear the content of the page
   
        else:
            st.warning('Incorrect username or password')
            return False


def app_home():
    st.title('Welcome to :red[JobLify]😄')
    
    st.subheader(':violet[Techie Job Search Simplified]👩‍💻')
    st.write('Please Login or Register to continue')
    st.image('i.gif', caption='Job Search',use_column_width=True)
# ...
def main():
    # If the user is logged in, show the job search app interface
    if st.session_state.get("logged_in", False):
        job_search_app()

        # Check if the user clicks 'Logout' in the job_search_app
        if 'action' in st.session_state and st.session_state.action == 'Logout':
            del st.session_state['logged_in']  # Remove the logged_in state
            del st.session_state['action']     # Remove the action state
            st.sidebar.empty()  # Clear the sidebar
            st.balloons()  # Show balloons for logout
            st.image('j.gif', caption='Job Search',use_column_width=False)
              # Redirect to the home page

    else:
        # If the user is not logged in, show the login/register/home options
        menu = st.sidebar.radio("Menu", ["Home","Login", "Register"])

        if menu == "Login":
            login()
        elif menu == "Register":
            register()
        elif menu == "Home":
            app_home()

# ... [rest of the code]



def job_search_app():
    st.sidebar.title("Choose Here!!!")
    selection = st.sidebar.radio("Go to", ["Home", "Visualizations", "Search for Jobs", "Logout"])

    if selection == "Logout":
        st.subheader('You have been logged out..  :green[Please Login again] 😊')
        st.session_state.action = 'Logout'
        return

    # Rest of the functionality goes here...

    # Your visualization and search functionality...
        # Load processed data for visualizations and search
    data = pd.read_csv('processed_data.csv')

    if selection == "Home":
        st.title('Job Search App')
        st.image('i.gif', caption='Job Search')
        st.write('Developed By:')
        st.write('Swapna Dande')
        st.write('Premonvitha Sai Rayana')
        st.write('@ Research and Analysis Interns')

    elif selection == "Visualizations":
        st.title('Visualizations')

        # Bar chart of unique value counts
        st.subheader('Number of Unique Values')
        unique_counts = data.nunique()
        st.bar_chart(unique_counts)

        # Horizontal bar plot of job salaries
        st.subheader('Job Salaries Plot')
        job_salary_counts = data['Job Salary'].value_counts().iloc[:10]
        fig1, ax1 = plt.subplots()
        ax1 = job_salary_counts.plot(kind='barh', colormap='Accent')
        plt.xlabel('No. of jobs')
        plt.ylabel('Salaries')
        st.pyplot(fig1)

        # Word cloud of key skills
        st.subheader('Word Cloud of Key Skills')
        common_words = ' '.join(data['Key Skills'].value_counts().index.ravel())
        wordcloud = WordCloud(width=1200, height=600, background_color='white', min_font_size=10).generate(common_words)
        fig2, ax2 = plt.subplots()
        ax2.imshow(wordcloud, interpolation='bilinear')
        ax2.axis('off')
        st.pyplot(fig2)

        # Bar charts of top 10 job titles with respective experience and salary
        st.subheader('Top 10 Popular Job Titles - Experience and Salary')
        for i in data['Job Title'].value_counts().index.tolist()[:10]:
            df = data[(data['Job Title'] == i) & (data['Job Salary'] != 'Not Disclosed by Recruiter')][['Job Salary','Job Experience Required']]
            fig = px.bar(df, x='Job Salary', y='Job Experience Required', color='Job Salary', height=400)
            st.plotly_chart(fig)

        # Sunburst chart of job salary and role category
        st.subheader('Sunburst Chart - Job Salary and Role Category')
        df1 = data[data['Job Salary'] != 'Not Disclosed by Recruiter'].sort_values('Job Salary',ascending=False)[['Job Salary','Role Category']]
        fig = px.sunburst(df1, path=['Role Category','Job Salary'])
        st.plotly_chart(fig)

        # Pie charts of job roles in top 10 locations
        st.subheader('Job Roles in Top 10 Locations')
        for i in data.Location.value_counts().index.tolist()[:10]:
            fig = px.pie(data[data.Location == i], names='Role Category', title = 'Job Roles in ' + i)
            st.plotly_chart(fig)

    elif selection == "Search for Jobs":
        st.title('Search for Jobs')
        st.image('image.jpg', caption='Job Search')
        search_term = st.text_input('Search by job title or keyword:')
        location = st.text_input('Location:')
        search_button = st.button('Search')

        # Search functionality
        if search_button:
            if search_term and location:
                filtered_data = data[
                    (data['Job Title'].str.contains(search_term, case=False)) &
                    (data['Location'].str.contains(location, case=False))
                ]
            elif search_term:
                filtered_data = data[
                    data['Job Title'].str.contains(search_term, case=False)
                ]
            elif location:
                filtered_data = data[
                    data['Location'].str.contains(location, case=False)
                ]
            else:
                filtered_data = None

            # Display the search results
            if filtered_data is not None and len(filtered_data) > 0:
                st.subheader(f'Found {len(filtered_data)} jobs')
                st.dataframe(filtered_data)
            elif filtered_data is not None:
                st.write('No jobs found based on the search criteria.')

    # ...

if __name__ == "__main__":
    main()
