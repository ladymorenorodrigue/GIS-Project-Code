"""
Final Project GIS 329
"""
import arcpy
import os
import pandas as pd
import matplotlib.pyplot as plt

# Set work space
workspace = r"Q:\\ladymorenorodriguez\\GIS329\\FINAL_PROJECT\\Phyton_Project\\Phyton_Project.gdb"
feature_class = r"Q:\\ladymorenorodriguez\\GIS329\\FINAL_PROJECT\\Phyton_Project\\Phyton_Project.gdb\\World_Countries_Generalized"
project_path = r"Q:\\ladymorenorodriguez\\GIS329\\FINAL_PROJECT\\Phyton_Project\\Phyton_Project.aprx"
output_folder = r"Q:\\ladymorenorodriguez\\GIS329\\FINAL_PROJECT\\Phyton_Project"
temperature_data = pd.read_csv(r"Q:\\ladymorenorodriguez\\GIS329\\FINAL_PROJECT\\Data\\Temperature_org.csv")
agriculture_data = pd.read_csv(r"Q:\\ladymorenorodriguez\\GIS329\\FINAL_PROJECT\\Data\\Land_org.csv")
flags_folder = r"Q:\\ladymorenorodriguez\\GIS329\\FINAL_PROJECT\\Flags"

# Set environment ArcGIS Pro
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True
aprx = arcpy.mp.ArcGISProject(project_path)
layout = aprx.listLayouts('Layout')[0]

# Get countries
countries = [row[0] for row in arcpy.da.SearchCursor(feature_class, ['COUNTRY'])]

# Make Feature Layer
layer = arcpy.MakeFeatureLayer_management(feature_class, "feature_layer")

# Make Plot
def create_plot(country):
    print(f"Generating Plot for: {country}")
    temp_country_data = temperature_data[temperature_data['Country Name'] == country]
    agri_country_data = agriculture_data[agriculture_data['Country Name'] == country]

    # Ask if there is data
    if temp_country_data.empty or agri_country_data.empty:
        print(f"There is no data for {country}. Next step.")
        return None

    # Make Plot
    fig, ax1 = plt.subplots(figsize=(8, 6))
    ax1.plot(temp_country_data['Year'], temp_country_data['Temperature'], color='tab:red', label='Temperature (°C)')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Temperature (°C)', color='tab:red')
    ax1.tick_params(axis='y', labelcolor='tab:red')

    ax2 = ax1.twinx()
    ax2.plot(agri_country_data['Year'], agri_country_data['Land_Use'], color='tab:blue', label='Land Use (%)')
    ax2.set_ylabel('Land Use (%)', color='tab:blue')
    ax2.tick_params(axis='y', labelcolor='tab:blue')

    ax1.set_title(f"Temperature vs Land Use in {country}")
    fig.tight_layout()

    # Save Plot with country's name
    plot_path = os.path.join(output_folder, f"{country.replace(' ', '_')}_temp_land_use.png")
    plt.savefig(plot_path)
    plt.close(fig)
    print(f"Plot save in: {plot_path}")
    return plot_path

# Loops for PDFs with Flags and Plots
for country_selected in countries:
    print(f"Processing country: {country_selected}")

    # Update Text in Layout
    for elm in layout.listElements("TEXT_ELEMENT"):
        if elm.name == "Text":
            elm.text = country_selected

    # Adjust name
    pais_escaped = country_selected.replace("'", "''")
    sql_expression = f"COUNTRY = '{pais_escaped}'"
    print(f"SQL Expression: {sql_expression}")

    # Select by attributes
    arcpy.management.SelectLayerByAttribute(layer, "NEW_SELECTION", sql_expression)

    # Get extension of the country
    map_frame = None
    for mf in layout.listElements("MAPFRAME_ELEMENT"):
        if mf.name == "Map Frame":
            map_frame = mf
            break

    if map_frame is None:
        print(f"There is not 'Map Frame'.")
        continue

    with arcpy.da.SearchCursor(feature_class, ['Shape@', 'COUNTRY']) as cursor:
        for row in cursor:
            if row[1] == country_selected:
                country_extent = row[0].extent
                map_frame.camera.setExtent(country_extent)
                print(f"Map frame update for {country_selected}.")
                break

    # Add Flag
    country_code = country_selected[:2].upper()
    flag_image_path = os.path.join(flags_folder, f"{country_code}.png")
    if os.path.exists(flag_image_path):
        for pic_elem in layout.listElements("PICTURE_ELEMENT"):
            if pic_elem.name == "Picture 1":
                pic_elem.sourceImage = flag_image_path
                pic_elem.elementPositionX = 4
                pic_elem.elementPositionY = 10.5
                pic_elem.width = 2
                pic_elem.height = 1.5
                print(f"Flag add to {country_selected}.")
                break
    else:
        print(f"There is no flag for {country_selected}.")

    # Create Plot with information (Land Use and Temperature)
    plot_path = create_plot(country_selected)
    if plot_path:
        for pic_elem in layout.listElements("PICTURE_ELEMENT"):
            if pic_elem.name == "Picture":
                pic_elem.sourceImage = plot_path
                pic_elem.elementPositionX = 4
                pic_elem.elementPositionY = 1.8
                pic_elem.width = 5
                pic_elem.height = 5
                print(f"Plot assigned to
                       {country_selected}.")
                break
    else:
        print(f"There is not Plot created {country_selected}.")

    # Export PDF for each country
    output_pdf_path = os.path.join(output_folder, f"{country_selected.replace(' ', '_')}.pdf")
    layout.exportToPDF(output_pdf_path)
    print(f"PDF was exported for {country_selected}: {output_pdf_path}")

print("All PDFs was generated. Finish Project GIS329.")