import openpyxl

# Create a new workbook
workbook = openpyxl.Workbook()

# Select the active sheet (assuming it's the first sheet)
sheet = workbook.active

# Write the column headings
sheet["A1"] = "Name"
sheet["B1"] = "Date"
sheet["C1"] = "Time"

# Save the workbook
workbook.save('attendance.xls')
