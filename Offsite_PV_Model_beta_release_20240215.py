# -*- coding: utf-8 -*-
"""
Author: Cheng Cheng ANU
Contact: Cheng.Cheng1@anu.edu.au
"""
import arcpy
from arcpy.sa import *
from arcpy.sa import *
from arcpy.sa import *
from arcpy.sa import *
from arcpy.sa import *
from arcpy.sa import *

def Offsite_PV_Model():  # Offsite_PV_Model

    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = False

    # Check out any necessary licenses.
    arcpy.CheckOutExtension("3D")
    arcpy.CheckOutExtension("spatial")
    arcpy.CheckOutExtension("ImageAnalyst")
    arcpy.CheckOutExtension("ImageExt")

    # Universal data
    Land_use = arcpy.Raster("clum_50m1220m")
    transmission_costs_by_land_use_types = "transmission costs by land use.csv"
    solar_costs_by_land_use_types = "solar costs by land use.csv"
    PV_Capacity_Factor = arcpy.Raster("PV_CF")

    # User Input 1: industry site coordinates 
    Industrial_site_point_ = "D:\\ArcGIS\\Projects\\PVDEH\\PVDEH.gdb\\Visy_Campbellfield"

    # User Input 2: search radius (km)
    input_buffer_distance = "50 Kilometers"

    # Process: Step 1: Reclass by Table (transmission) (Reclass by Table) (sa)
    transmission_costs = "D:\\ArcGIS\\Projects\\PVDEH\\PVDEH.gdb\\transmission_costs"
    Step_1_Reclass_by_Table_transmission_ = transmission_costs
    transmission_costs = arcpy.sa.ReclassByTable(Land_use, transmission_costs_by_land_use_types, "Tertiary code", "Tertiary code", "Transmission_costs", "DATA")
    transmission_costs.save(Step_1_Reclass_by_Table_transmission_)

    # Process: Step 2: Reclass by Table (solar) (Reclass by Table) (3d)
    solar_costs = "D:\\ArcGIS\\Projects\\PVDEH\\PVDEH.gdb\\solar_costs"
    arcpy.sa.ReclassByTable(in_raster=Land_use, in_remap_table=solar_costs_by_land_use_types, from_value_field="Tertiary code", to_value_field="Tertiary code", output_value_field="Solar_costs", out_raster=solar_costs)
    solar_costs = arcpy.Raster(solar_costs)

    # Process: Step 3: Reclassify (Reclassify) (sa)
    unsuitable_area_binary = "D:\\ArcGIS\\Projects\\PVDEH\\PVDEH.gdb\\unsuitable_area_binary"
    Step_3_Reclassify = unsuitable_area_binary
    unsuitable_area_binary = arcpy.sa.Reclassify(solar_costs, "VALUE", "0 1 0;1 9999 1", "DATA")
    unsuitable_area_binary.save(Step_3_Reclassify)
    
    # Process: Step 4: Buffer (Buffer) (analysis)
    site_buffer = "D:\\ArcGIS\\Projects\\PVDEH\\PVDEH.gdb\\site_buffer"
    arcpy.analysis.Buffer(in_features=Industrial_site_point_, out_feature_class=site_buffer, buffer_distance_or_field=input_buffer_distance)

    # Process: Step 5: Distance Accumulation (Distance Accumulation) (sa)
    optimal_transmission_distance = "D:\\ArcGIS\\Projects\\PVDEH\\PVDEH.gdb\\transmission_distance"
    Step_5_Distance_Accumulation = optimal_transmission_distance
    transmission_backdirection = "D:\\ArcGIS\\Projects\\PVDEH\\PVDEH.gdb\\transmission_backdirection"
    Out_source_direction_raster = ""
    Out_source_location_raster = ""
    optimal_transmission_distance = arcpy.sa.DistanceAccumulation(Industrial_site_point_, "", "", transmission_costs, "", "BINARY 1 -30 30", "", "BINARY 1 45", transmission_backdirection, Out_source_direction_raster, Out_source_location_raster, "", "", "", "", "PLANAR")
    optimal_transmission_distance.save(Step_5_Distance_Accumulation)

    transmission_backdirection = arcpy.Raster(transmission_backdirection)

    # Process: Step 6: Clip Raster (Clip Raster) (management)
    transmission_distance_Clip = "D:\\ArcGIS\\Projects\\PVDEH\\PVDEH.gdb\\transmission_distance_Clip"
    arcpy.management.Clip(in_raster=optimal_transmission_distance, rectangle="1145819.7126 -4173941.3043 1145819.7126 -4173941.3043", out_raster=transmission_distance_Clip, in_template_dataset=site_buffer, clipping_geometry="ClippingGeometry")
    transmission_distance_Clip = arcpy.Raster(transmission_distance_Clip)


    # Process: Step 7: Raster Calculator (calculation of indicative cost) (Raster Calculator) (sa)
    raw_indicative_cost_heat_map_ = "D:\\ArcGIS\\Projects\\PVDEH\\PVDEH.gdb\\raw_cost"
    Step_7_Raster_Calculator_calculation_of_indicative_cost_ = raw_indicative_cost_heat_map_
    raw_indicative_cost_heat_map_ = Con(transmission_distance_Clip<1000,
                                         (4879*1.42*transmission_distance_Clip/1000/13.78+4879*1.42*transmission_distance_Clip/1000*0.01+solar_costs*1000/13.78+17*1000)
                                         /("PV_CF"*8760*(1-0.03*transmission_distance_Clip/100000)),
                                         Con(transmission_distance_Clip<5000,
                                             (4879*1.23*transmission_distance_Clip/1000/13.78+4879*1.23*transmission_distance_Clip/1000*0.01+solar_costs*1000/13.78+17*1000)
                                             /("PV_CF"*8760*(1-0.03*transmission_distance_Clip/100000)),
                                             Con(transmission_distance_Clip<10000,(4879*1.07*transmission_distance_Clip/1000/13.78+4879*1.07*transmission_distance_Clip/1000*0.01+
                                                                                      solar_costs*1000/13.78+17*1000)
                                                 /("PV_CF"*8760*(1-0.03*transmission_distance_Clip/100000)),
                                                 Con(transmission_distance_Clip<100000,
                                                     (4879*transmission_distance_Clip/1000/13.78+4879*transmission_distance_Clip/1000*0.01+solar_costs*1000/13.78+17*1000)
                                                     /("PV_CF"*8760*(1-0.03*transmission_distance_Clip/100000)),
                                                     Con(transmission_distance_Clip<200000,(4879*0.96*transmission_distance_Clip/1000/13.78+4879*0.96*transmission_distance_Clip/1000*0.01
                                                                                               +solar_costs*1000/13.78+17*1000)
                                                         /("PV_CF"*8760*(1-0.03*transmission_distance_Clip/100000)),
                                                         (4879*0.93*transmission_distance_Clip/1000/13.78+4879*0.93*transmission_distance_Clip/1000*0.01+solar_costs*1000/13.78+17*1000)
                                                         /("PV_CF"*8760*(1-0.03*transmission_distance_Clip/100000))))))) * unsuitable_area_binary
    raw_indicative_cost_heat_map_.save(Step_7_Raster_Calculator_calculation_of_indicative_cost_)


    # Process: Step 8: Raster Calculator (convert to integer) (Raster Calculator) (sa)
    integer_indicative_cost = "D:\\ArcGIS\\Projects\\PVDEH\\PVDEH.gdb\\int_cost"
    Step_8_Raster_Calculator_convert_to_integer_ = integer_indicative_cost
    integer_indicative_cost = Int( "%raw_cost%"*100)
    integer_indicative_cost.save(Step_8_Raster_Calculator_convert_to_integer_)


    # Process: Step 9: Zonal Statistics as Table (Zonal Statistics as Table) (sa)
    summary_table = "D:\\ArcGIS\\Projects\\PVDEH\\PVDEH.gdb\\summary_table"
    Output_Join_Layer = ""
    arcpy.sa.ZonalStatisticsAsTable(integer_indicative_cost, "Value", integer_indicative_cost, summary_table, "DATA", "ALL", "CURRENT_SLICE", [90], "AUTO_DETECT", "ARITHMETIC", 360, Output_Join_Layer)
    .save(Step_9_Zonal_Statistics_as_Table)


if __name__ == '__main__':
    # Global Environment settings
    with arcpy.EnvManager(scratchWorkspace="D:\\ArcGIS\\Projects\\PVDEH\\PVDEH.gdb", workspace="D:\\ArcGIS\\Projects\\PVDEH\\PVDEH.gdb"):
        Offsite_PV_Model()
