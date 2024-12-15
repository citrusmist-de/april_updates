
import streamlit as st
import pandas as pd
import io

st.set_page_config(layout="wide")

def create_table(columns, num_rows):
    """Function to create a blank table with specific columns and number of rows."""
    return pd.DataFrame(columns=columns, index=range(num_rows))

def combine_tables(tables):
    """Function to combine multiple tables using a Cartesian join (cross join)."""
    combined_df = tables[0]  # Start with the first table
    combined_df = combined_df.dropna(how='all')    
    # Perform cross join by concatenating tables side by side
    for table in tables[1:]:
        table = table.dropna(how='all')
        combined_df = pd.merge(combined_df, table, how='cross')
    
    return combined_df

def add_index_column(df):
    df_with_index = df.copy()  # Copy the original DataFrame to avoid modifying the original
    df_with_index.insert(0, 'index', range(1, len(df) + 1))  # Sequential index from 1 to nrow    
    return df_with_index

def download_csv(df, filename="data.csv"):
    """
    Function to allow downloading a pandas DataFrame as a CSV file.
    Takes a DataFrame as an argument and generates a download button.
    """
    # Convert DataFrame to CSV
    csv_data = df.to_csv(index=False)
    
    # Create the download button in Streamlit
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name=filename,
        mime="text/csv"
    )

def main():
    st.markdown(
    """
    <h3 style="color: #007BA7;">Combinatorial Table Generator 🐡</h3>
    """, 
    unsafe_allow_html=True
    )

    st.markdown(
    """
    <h4 style="color: #007BA7;"><hr>Turn multiple lists into a table with all possible rowwise combinations of those lists.<br><br></h4>
    """, 
    unsafe_allow_html=True
    )
    # Add a radio button for selecting default column names or no column names
    column_option = st.radio("Choose column name setting", 
                             ("Use default column names", "No default column names"))
    add_index = st.radio("Add 'index' column?:", ("Yes", "No"))
    
    # Allow user to choose the number of tables
    num_tables = st.number_input("Select number of tables", min_value=1, max_value=10, value=2)

    # Dynamically create default columns based on the number of tables
    if column_option == "Use default column names":
        default_columns = [["col1", "col2", "col3"]] * num_tables  # Create default columns for each table
    else:
        default_columns = [[]] * num_tables  # No default column names for each table

    # Initialize lists to store tables
    col1_tables = []

    # Loop through each table to allow column names and number of rows
    for table_idx in range(num_tables):
        st.subheader(f"Table {table_idx + 1}")
        
        # Input for column names
        if default_columns[table_idx]:
            columns = default_columns[table_idx]  # Use the default column names
        else:
            columns = st.text_input(f"Enter column names for Table {table_idx + 1} (comma separated)", 
                                    value="Column1, Column2, Column3", key=f"columns_{table_idx}")
            columns = [col.strip() for col in columns.split(",")]  # Split and strip input string into column names
        
        # Input for the number of rows
        num_rows = 10000

        # Create the table and allow the user to paste values using the data editor
        table = create_table(columns, num_rows)
        
        # Render the data editor and get the edited data
        edited_table = st.data_editor(pd.DataFrame(table), key=f"table_{table_idx}", num_rows="dynamic")

        # Check if the returned table is a valid DataFrame and not empty
        if isinstance(edited_table, pd.DataFrame):
            if not edited_table.empty:  # Ensure the DataFrame is not empty
                edited_table = edited_table.dropna(axis=1, how='all')

                col1_tables.append(edited_table)  # Add to col1_tables for cross join
            else:
                st.warning(f"Table {table_idx + 1} is empty. Please enter data.")
        else:
            st.error(f"Table {table_idx + 1} was not correctly edited. Please ensure valid data.")
    calc_opt = st.radio("Calculate table with all row combinations from above table:", options = ['I\'m still editing the inputs', 'Calculate combinations'])
    # Combine the tables if needed
    if calc_opt == "Calculate combinations":
        if len(col1_tables) > 1:
            # Combine tables from col1 using Cartesian join (cross join)
            combined_df = combine_tables(col1_tables)
            if add_index == "Yes":
                combined_df = add_index_column(combined_df)
            combined_df = combined_df.dropna(axis=1, how='all')

            st.write("### Combinatorial Table")            
            st.write(combined_df)
            num_rows, num_cols = combined_df.shape            
            st.write(f"Table has {num_rows} rows and {num_cols} columns.") 
            st.session_state['combined_df'] = combined_df  # Only save combined_df in session state
            download_csv(combined_df)
        else:
            st.warning("Please add more than one table to combine.")

    # Allow the user to edit the combined table, if available
    # if 'combined_df' in st.session_state and not st.session_state['combined_df'].empty:
    #     st.subheader("Edit Combined Table")
    #     d_addmorerows = st.session_state['combined_df']
    #     d_modded = st.data_editor(d_addmorerows, num_rows="dynamic", key="combined_table_edit")


if __name__ == "__main__":
    main()
