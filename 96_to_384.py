
import streamlit as st
import pandas as pd
import numpy as np
import openpyxl
from io import BytesIO

# Function to transform the plate data
def transform_plate(input_data):
    original_header = list(input_data[0])  # Store the first row as header
    
    plate_96 = pd.DataFrame(input_data)
    plate_96 = plate_96.drop(index=0).reset_index(drop=True)  # Drop first row (header)
    plate_96 = plate_96.drop(columns=0).reset_index(drop=True)  # Drop first column (index column)
    
    # Reverse the rows
    plate_96_sorted = plate_96.iloc[::-1].reset_index(drop=True)
    
    # Add blank rows between each row
    plate_96_with_gaps = []
    for _, row in plate_96_sorted.iterrows():
        plate_96_with_gaps.append(row.values.tolist())
        plate_96_with_gaps.append([None] * len(row))
    
    plate_96_with_gaps = pd.DataFrame(plate_96_with_gaps)
    
    # Rotate 90 degrees
    plate_384_rotated = plate_96_with_gaps.transpose().reset_index(drop=True)
    
    # Shift every other row by one cell
    for i in range(1, len(plate_384_rotated), 2):
        plate_384_rotated.iloc[i] = plate_384_rotated.iloc[i].shift(1)
    
    # Ensure exactly 16 data rows
    while len(plate_384_rotated) < 16:
        plate_384_rotated.loc[len(plate_384_rotated)] = [None] * plate_384_rotated.shape[1]
    
    # Determine the highest numeric column in the original header and extend to 24
    max_numeric = max([int(x) for x in original_header[1:] if str(x).isdigit()], default=0)
    new_columns = [original_header[0]] + [str(i) for i in range(1, 25)]
    
    # Ensure exactly 25 total columns
    plate_384_rotated = plate_384_rotated.reindex(columns=range(25))
    plate_384_rotated.columns = new_columns[:25]
    
    # Add row labels A-P in column 1, starting in the first row below the header row
    rows = list("ABCDEFGHIJKLMNOP")[:16]
    plate_384_rotated.iloc[:16, 0] = rows
    # Extract data as a NumPy array
    sub_array = plate_384_rotated.iloc[0:14, 1:15].to_numpy()

    # Clear the original section
    plate_384_rotated.iloc[0:14, 1:15] = None  # Replace with None (or '' for empty)

    # Paste it 1 row down and 1 column to the right
    plate_384_rotated.iloc[1:15, 2:16] = sub_array  # Assign back to new location

    return plate_384_rotated

def main():
    st.title("Plate Transformation Tool")
    
    st.markdown("""
    Upload a 96-well plate (8x12 format), and this tool will transform it into a 384-well format (16x24),
    ensuring the final output has 24 columns and 17 rows.
    """)
    
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    
    if uploaded_file is not None:
        try:
            input_data = pd.read_csv(uploaded_file, header=None)
            st.subheader("Original Plate Data")
            st.write(input_data)
            
            output_plate = transform_plate(input_data.values)
            st.subheader("Transformed Plate Data")
            st.write(output_plate)
            
            # Convert the DataFrame to an Excel file in memory
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                output_plate.to_excel(writer, index=False, sheet_name="Transformed Data")
            output.seek(0)  # Move to the beginning of the file

            # Add a download button
            st.download_button(
                label="Download as Excel",
                data=output,
                file_name="transformed_plate.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            st.error(f"Error processing the file: {e}")

if __name__ == "__main__":
    main()








