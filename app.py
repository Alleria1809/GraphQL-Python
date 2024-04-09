import streamlit as st
from backend import resolve_find_plan, resolve_insert_new_plan   # Import the resolver
from uuid import UUID
from datetime import datetime
from dateutil import parser

# Streamlit UI
st.title("Add Plans to My Schedule Today")

# Streamlit UI for Adding New Plans
st.header("Add a New Plan")

# Form for new plan data
with st.form(key='new_plan_form'):
    user_id = st.number_input("User ID", min_value=1, value=2009, format="%d")
    created_at = st.text_input("Creation Date and Time (YYYY-MM-DD HH:MM:SS)", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    event_type = st.text_input("Event Type", value="add new task")
    task_content = st.text_area("Task Content")
    
    # Submit button for the form
    submit_button = st.form_submit_button(label='Insert New Plan')

if submit_button:
    try:
        # Inserting the new plan using the resolver
        new_plan = resolve_insert_new_plan(None, None, int(user_id), created_at, event_type, task_content)
        
        # Displaying a success message
        st.success(f"Successfully added new plan with ID: {new_plan['plan_id']}")
    except Exception as e:
        st.error(f"Error adding new plan: {e}")



# Streamlit UI for Querying Historical Plans
st.header("Query Historical Plans")

# User input for user ID
user_id_query = 2009

# User input for date
date_query = st.text_input("Enter date (YYYY-MM-DD) to query plans:", value=datetime.now().strftime("%Y-%m-%d"))

# Button to trigger the query
if st.button('Query Plans'):
    try:
        # Parsing the user input to date
        date = parser.parse(date_query).strftime("%Y-%m-%d")
        
        # Using the resolver to query plans based on user ID and date
        activities = resolve_find_plan(None, None, user_id_query, date)
        
        # Display the activities
        if activities:
            for activity in activities:
                st.write(f"Activity Session ID: {activity.session_id}, Created At: {activity.created_at.strftime('%Y-%m-%d %H:%M:%S')}, Task Content: {activity.task_content}")
        else:
            st.write("No activities found for this user on the specified date.")
    except Exception as e:
        st.error(f"Error querying activities: {e}")

