import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import sqlite3

# --- DATABASE SETUP ---
conn = sqlite3.connect('tasks.db', check_same_thread=False)
c = conn.cursor()

def create_table():
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  task TEXT,
                  priority TEXT,
                  status TEXT)''')
    conn.commit()

def add_task_db(task, priority, status):
    c.execute('INSERT INTO tasks (task, priority, status) VALUES (?, ?, ?)', (task, priority, status))
    conn.commit()

def get_all_tasks():
    c.execute('SELECT * FROM tasks')
    data = c.fetchall()
    return pd.DataFrame(data, columns=['ID', 'Task', 'Priority', 'Status'])

def update_task_db(task_id, task, priority, status):
    c.execute('UPDATE tasks SET task=?, priority=?, status=? WHERE id=?', (task, priority, status, task_id))
    conn.commit()

def delete_task_db(task_id):
    c.execute('DELETE FROM tasks WHERE id=?', (task_id,))
    conn.commit()

create_table()

# --- STREAMLIT APP ---

def clear_inputs():
    add_task_db(task, option, status1)
    st.session_state['tsk'] = ""
    st.session_state['opt'] = "High"
    st.session_state['chk'] = False
    st.success("Task Added Successfully!")
    st.rerun()

def edit_task(task1, priority1, status1, task_id):
    task2 = st.text_input("Edit Task:", value=task1, key='tsk1')
    option2 = st.selectbox('Edit Priority:', ('High', 'Medium', 'Low'), index=['High', 'Medium', 'Low'].index(priority1), key="opt1")
    status2 = st.checkbox("Completed?", value=(status1 == "Completed 😉"), key="chk1")

    if st.button("Update Task"):
        new_status = "Completed 😉" if status2 else "Pending 😡"
        update_task_db(task_id, task2, option2, new_status)
        st.success("✅ Task Updated Successfully!")
        st.rerun()

selected = option_menu(
    menu_title=None,
    options=["Home", "Tasks", "History", "Analysis"],
    icons=['house', 'list-task', 'clock-history', 'bar-chart'],
    menu_icon='cast',
    default_index=0,
    orientation='horizontal',
    styles={}
)

if selected == 'Home':
    st.title(f"Welcome to To-Do App ✌️.")
    task = st.text_input("Enter Your Task:", key='tsk')

    option = st.selectbox(
        'Select Priority:',
        ('High', 'Medium', 'Low'),
        key="opt"
    )
    st.write(f'You selected: {option}')

    status = st.checkbox(label="Status", key="chk")
    status1 = "Completed 😉" if status else "Pending 😡"

    if st.button("Add Task", on_click=clear_inputs):
        pass

if selected == 'Tasks':
    st.title("📋 Your Tasks List")
    df_display = get_all_tasks()
    df_display.index = range(1, len(df_display) + 1)
    st.dataframe(df_display[['Task', 'Priority', 'Status']])

    with st.sidebar:
        selected1 = option_menu(
            menu_title="Edit",
            options=["Edit Task", "Delete Task"],
            icons=['pencil-square', 'trash'],
            menu_icon='cast',
            default_index=0,
        )

        if selected1 == 'Edit Task':
            st.title(f"Edit Your Task")
            no = st.text_input("Enter the Task ID to Edit:")
            if no:
                try:
                    task_id = int(no)
                    df = get_all_tasks()
                    if task_id in df['ID'].values:
                        task_row = df[df['ID'] == task_id]
                        task1 = task_row['Task'].values[0]
                        priority1 = task_row['Priority'].values[0]
                        status1 = task_row['Status'].values[0]

                        edit_task(task1, priority1, status1, task_id)
                    else:
                        st.error("Invalid Task ID")
                except ValueError:
                    st.error("Please enter a valid ID number.")

        if selected1 == 'Delete Task':
            st.title(f"Delete Your Task")
            no = st.text_input("Enter the Task ID to Delete:")
            if no:
                try:
                    task_id = int(no)
                    df = get_all_tasks()
                    if task_id in df['ID'].values:
                        if st.button("Delete Task"):
                            delete_task_db(task_id)
                            st.success("🗑️ Task Deleted Successfully!")
                            st.rerun()
                    else:
                        st.error('Please enter a valid Task ID.')
                except ValueError:
                    st.error("❌ Please enter a valid number.")

if selected == 'History':
    st.title("📜 Task History")
    df = get_all_tasks()
    st.dataframe(df[['Task', 'Priority', 'Status']])

if selected == 'Analysis':
    st.title("📊 Task Analysis")
    df = get_all_tasks()
    st.write(f"Total Tasks: {len(df)}")
    st.write(f"✅ Completed: {len(df[df['Status'] == 'Completed 😉'])}")
    st.write(f"⏳ Pending: {len(df[df['Status'] == 'Pending 😡'])}")
