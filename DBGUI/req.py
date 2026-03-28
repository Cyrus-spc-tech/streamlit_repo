st.subheader(f"Insert Data into {selected_table}")
    columns_info = db.get_table_columns(selected_table)
    input_data = {}
    
    for col in columns_info:
        if col['name'] != 'id' or col['extra'] != 'auto_increment':
            col_name = col['name']
            col_type = col['type'].lower()
            
            if 'int' in col_type:
                input_data[col_name] = st.number_input(f"{col_name} ({col['type']})", value=0, step=1)
            elif 'float' in col_type or 'decimal' in col_type:
                input_data[col_name] = st.number_input(f"{col_name} ({col['type']})", value=0.0, step=0.1)
            elif 'boolean' in col_type:
                input_data[col_name] = st.checkbox(f"{col_name} ({col['type']})")
            elif 'password' in col_name.lower():
                input_data[col_name] = st.text_input(f"{col_name} ({col['type']})", type="password")
            elif 'text' in col_type:
                input_data[col_name] = st.text_area(f"{col_name} ({col['type']})")
            elif 'datetime' in col_type or 'date' in col_type:
                input_data[col_name] = st.text_input(f"{col_name} ({col['type']})", value="2024-01-01")
            else:
                input_data[col_name] = st.text_input(f"{col_name} ({col['type']})")
    
    if st.button("Insert"):
        if input_data:
            if db.insert_into_custom_table(selected_table, input_data):
                st.success("Data inserted successfully!")
            else:
                st.error("Failed to insert data.")
        else:
            st.warning("Please fill at least one field.")

elif choice == "View All Data":
    st.subheader(f"All Data from {selected_table}")
    
    data = db.fetch_custom_table(selected_table)
    
    if data is not None and not data.empty:
        st.dataframe(data, use_container_width=True)
        
        # Export options
        csv = data.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"{selected_table}_data.csv",
            mime="text/csv"
        )
    else:
        st.info("No data found in this table.")

elif choice == "Table Structure":
    st.subheader(f"Structure of {selected_table}")
    
    structure = db.describe_custom_table(selected_table)
    
    if structure is not None:
        st.dataframe(structure, use_container_width=True)
    else:
        st.error("Could not fetch table structure.")

elif choice == "Update Record":
    st.subheader(f"Update Record in {selected_table}")
    
    record_id = st.number_input("Enter Record ID to Update", min_value=1, step=1)
    
    # Show current record
    current_record = db.get_record_by_id(selected_table, record_id)
    if current_record:
        st.write("Current Record:")
        st.json(current_record)
        
        # Get table columns for update form
        columns_info = db.get_table_columns(selected_table)
        update_data = {}
        
        for col in columns_info:
            if col['name'] != 'id':  # Don't update ID
                col_name = col['name']
                col_type = col['type'].lower()
                
                # Show current value and allow update
                current_value = current_record.get(col_name, '')
                
                if 'int' in col_type:
                    update_data[col_name] = st.number_input(
                        f"Update {col_name} ({col['type']})", 
                        value=int(current_value) if current_value else 0, 
                        step=1,
                        key=f"update_{col_name}"
                    )
                elif 'float' in col_type or 'decimal' in col_type:
                    update_data[col_name] = st.number_input(
                        f"Update {col_name} ({col['type']})", 
                        value=float(current_value) if current_value else 0.0, 
                        step=0.1,
                        key=f"update_{col_name}"
                    )
                elif 'boolean' in col_type:
                    update_data[col_name] = st.checkbox(
                        f"Update {col_name} ({col['type']})", 
                        value=bool(current_value),
                        key=f"update_{col_name}"
                    )
                elif 'password' in col_name.lower():
                    update_data[col_name] = st.text_input(
                        f"Update {col_name} ({col['type']})", 
                        value=str(current_value), 
                        type="password",
                        key=f"update_{col_name}"
                    )
                elif 'text' in col_type:
                    update_data[col_name] = st.text_area(
                        f"Update {col_name} ({col['type']})", 
                        value=str(current_value),
                        key=f"update_{col_name}"
                    )
                else:
                    update_data[col_name] = st.text_input(
                        f"Update {col_name} ({col['type']})", 
                        value=str(current_value),
                        key=f"update_{col_name}"
                    )
        
        if st.button("Update Record"):
            if db.update_record(selected_table, record_id, update_data):
                st.success("Record updated successfully!")
            else:
                st.error("Failed to update record.")
    else:
        st.warning("Record not found. Please enter a valid ID.")

elif choice == "Delete Record":
    st.subheader(f"Delete Record from {selected_table}")
    
    record_id = st.number_input("Enter Record ID to Delete", min_value=1, step=1)
    
    # Show record before deletion
    current_record = db.get_record_by_id(selected_table, record_id)
    if current_record:
        st.write("Record to be deleted:")
        st.json(current_record)
        
        if st.button("Delete Record", type="primary"):
            db.delete_from_custom_table(selected_table, record_id)
            st.success("Record deleted successfully!")
    else:
        st.warning("Record not found. Please enter a valid ID.")

elif choice == "Get Record by ID":
    st.subheader(f"Get Record from {selected_table}")
    
    record_id = st.number_input("Enter Record ID", min_value=1, step=1)
    
    if st.button("Fetch Record"):
        record = db.get_record_by_id(selected_table, record_id)
        if record:
            st.success("Record found!")
            st.json(record)
        else:
            st.warning("Record not found.")

elif choice == "Create Custom Table":
    st.subheader("Create Custom Table")
    
    table_name = st.text_input("Table Name")
    
    st.write("Add columns :")
    columns = []
    num_columns = st.number_input("Number of columns", min_value=1, max_value=20, value=3)
    
    for i in range(num_columns):
        col_name = st.text_input(f"Column {i+1} Name", key=f"col_name_{i}")
        col_type = st.selectbox(
            f"Column {i+1} Type", 
            ['int', 'varchar', 'text', 'float', 'datetime', 'boolean'],
            key=f"col_type_{i}"
        )
        if col_name:
            columns.append((col_name, col_type))
    
    if st.button("Create Table"):
        if table_name and columns:
            columns_dict = {name: dtype for name, dtype in columns}
            if db.create_custom_table(table_name, columns_dict):
                st.success(f"Table '{table_name}' created successfully!")
                st.rerun()  # Refresh to show new table in sidebar
            else:
                st.error("Failed to create table.")
        else:
            st.warning("Please enter table name and at least one column.")

elif choice == "Visualize Data":
    st.subheader(f"Visualize Data from {selected_table}")
    
    data = db.fetch_custom_table(selected_table)
    
    if data is not None and not data.empty:
        st.dataframe(data, use_container_width=True)
        
        # Basic statistics
        st.subheader("Data Statistics")
        st.write(data.describe())
        
        # Visualizations for numeric columns
        numeric_columns = data.select_dtypes(include=['number']).columns
        if len(numeric_columns) > 0:
            st.subheader("Numeric Columns Visualization")
            selected_col = st.selectbox("Select column for visualization", numeric_columns)
            
            if selected_col:
                st.bar_chart(data[selected_col])
        
        # Value counts for categorical columns
        text_columns = data.select_dtypes(include=['object']).columns
        if len(text_columns) > 0:
            st.subheader("Categorical Columns Analysis")
            selected_text_col = st.selectbox("Select text column for analysis", text_columns)
            
            if selected_text_col:
                value_counts = data[selected_text_col].value_counts()
                st.bar_chart(value_counts)