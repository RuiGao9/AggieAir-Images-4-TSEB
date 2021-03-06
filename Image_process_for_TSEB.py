import numpy as np
import arcpy
from matplotlib import pyplot as plt


# Modify the path below accordingly
%run ...\CanopyHeight_Vine.py
help(CanopyHeight_Vine)
%run ...\CanopySoilTemperatureSeparation_Vine.py
help(CanopySoilTemperatureSeparation_Vine)
%run ...\TellResolution.py
help(TellResolution)
%run ...\TellTheGeoInfo.py
help(TellTheGeoInfo)
%run ...\FolderCreater.py
%run ...\WriteTiffData.py
help(WriteTiffData)
%run ...\TellExtent.py
help(TellExtent)

# 1. Inputs info
# fishnet: domain size is 3.6 meter by 3.6 meter in this case
file_grids = r'...\Fish_RIP_180806_1041_720.shp'
# LAI map: resolution for this map is 3.6 meter by 3.6 meter in this case
file_LAI = r'...\LAI_RIP_180806_1041_720.tif'
# Optical image containing R, G, B, and NIR: resolution is 0.1 meter by 0.1 meter
file_RGBN = r'...\RGB.tif'
# DSM data: resolution is 0.1 meter by 0.1 meter
file_DSM = r'...\DSM.tif'
# raw data gained from the AggieAir platform, and a constant resolution for this image is not required
file_tmp = r'...\Thermal.tif'

# create a folder to save all the results (including mid-products)
folder_output = r'...\NewFolderForSaving'
FolderCreater(folder_output)

# parameters (some of them need to be adjusted accordingly, e.g., threshold_veg and threshold_soil)
[band_R, band_G, band_B, band_N] = [0, 1, 2, 3]
threshold_veg, threshold_soil, threshold_veg_height, threshold_grid, resolution_rgb_dsm, resolution_grid, resolution_tmp, resolution_tmp_2t = 0.62, 0.45, 1.4, 3.6, 0.1, 3.6, 0.6, 0.1
threshold_thermal_upscale_ratio = "6"
extent_LAI = TellExtent(file_LAI)

# 2. Generate R, G, B, NIR, and DSM images
# Align the optical image as the LAI frame
rgbn_alined_name = "RGBN_Alined.tif"
arcpy.Clip_management(in_raster=file_RGBN, 
                      rectangle=extent_LAI, 
                      out_raster=folder_output + "//" + rgbn_alined_name, 
                      in_template_dataset=file_LAI, 
                      nodata_value="-3.402823e+38", 
                      clipping_geometry="NONE", 
                      maintain_clipping_extent="MAINTAIN_EXTENT")
# aline DSM image
dsm_alined_name = "DSM_Alined.tif"
arcpy.Clip_management(in_raster=file_DSM, 
                      rectangle=extent_LAI, 
                      out_raster=folder_output + "//" + dsm_alined_name, 
                      in_template_dataset=file_LAI, 
                      nodata_value="-3.402823e+38", 
                      clipping_geometry="NONE", 
                      maintain_clipping_extent="MAINTAIN_EXTENT")
# read RGBNIR data
raster_RGB = arcpy.RasterToNumPyArray(folder_output + "//" + rgbn_alined_name, nodata_to_value=-9999)
print(raster_RGB.shape)
# read RGBNIR image
(res_x,res_y) = TellResolution(folder_output + "//" + rgbn_alined_name)
[RGB_dims,RGB_img_geo,RGB_img_prj] = TellTheGeoInfo(folder_output + "//" + rgbn_alined_name)
extent_RGB = TellExtent(folder_output + "//" + rgbn_alined_name)
print("Resolution is:",res_x,res_y,"\nDimension is:",RGB_dims)
# get R and NIR
raster_R = raster_RGB[band_R,:,:]
raster_NIR = raster_RGB[band_N,:,:]
WriteTiffData(folder_output, "Red", RGB_dims[0], RGB_dims[1], raster_R, RGB_img_geo, RGB_img_prj)
WriteTiffData(folder_output, "NIR", RGB_dims[0], RGB_dims[1], raster_NIR, RGB_img_geo, RGB_img_prj)
# calculate the NDVI
raster_ndvi = (raster_NIR-raster_R)/(raster_NIR+raster_R)
# show NDVI map
plt.imshow(raster_ndvi, interpolation='nearest')
plt.show()
# write NDVI
WriteTiffData(folder_output, "NDVI", RGB_dims[0], RGB_dims[1], raster_ndvi, RGB_img_geo,RGB_img_prj)

# 3. Fractional cover
# show the histogram of the NDVI
raster_ndvi[raster_ndvi<0] = np.nan
plt.hist(raster_ndvi)
plt.show()
# show the classification figure
raster_ndvi[raster_ndvi<=threshold_veg] = 0
raster_ndvi[raster_ndvi>0] = 1
plt.hist(raster_ndvi)
plt.show()
# Classification: vegetation and soil
WriteTiffData(folder_output, "Veg_Soil", RGB_dims[0], RGB_dims[1], raster_ndvi, RGB_img_geo, RGB_img_prj)
# Zonal statistical
arcpy.gp.ZonalStatistics_sa(file_grids, 
                            "FID", 
                            folder_output + "\\" + "Veg_Soil.tif", 
                            folder_output + "\\Veg_Soil_pixel.tif", 
                            "SUM", "DATA")
# Upgrade resolution from 0.1 meter to 3.6 meter
arcpy.gp.Aggregate_sa(folder_output + "\\Veg_Soil_pixel.tif", 
                      folder_output + "\\Veg_Aggregate.tif", 
                      "36", 
                      "MEAN", "EXPAND", "DATA")
(res_x,res_y) = TellResolution(folder_output + "\\Veg_Aggregate.tif")
[fc_dims,fc_img_geo,fc_img_prj] = TellTheGeoInfo(folder_output + "\\Veg_Aggregate.tif")
extent_fc = TellExtent(folder_output + "\\Veg_Aggregate.tif")
# calculate the fractional cover
raster_fc = arcpy.RasterToNumPyArray(folder_output + "\\Veg_Aggregate.tif", nodata_to_value=np.nan)
raster_fc = raster_fc/((resolution_grid/resolution_rgb_dsm)**2)
# output the result as an image
WriteTiffData(folder_output, "Fractional_Cover", fc_dims[0], fc_dims[1], raster_fc, fc_img_geo, fc_img_prj)

# 4. Canopy width
raster_cw = raster_fc * resolution_grid
WriteTiffData(folder_output, "Canopy_Width", fc_dims[0], fc_dims[1], raster_cw, fc_img_geo, fc_img_prj)

# 5. Canopy height
# the frame of the DSM, Red, NIR, and LAI should be the same.
NoDataValue = np.nan
CanopyHeight_Vine(file_LAI, folder_output + "//" + dsm_alined_name, folder_output+"\\Red.tif", folder_output+"\\NIR.tif", 
                  NoDataValue, threshold_veg, threshold_soil, threshold_veg_height,
                  folder_output, "Canopy_Height.tif")
                  
# 6. Canopy width over canopy height
# Aline the canopy height with the canopy width
canopy_height_alined_name = "Canopy_Height_Alined.tif"
extent_cw = TellExtent(folder_output + "//" + "Canopy_Width.tif")
arcpy.Clip_management(in_raster=folder_output + "//" + "Canopy_Height.tif", 
                      rectangle=extent_cw, 
                      out_raster=folder_output + "//" + canopy_height_alined_name, 
                      in_template_dataset=folder_output + "//" + "Canopy_Width.tif", 
                      nodata_value="-3.402823e+38", 
                      clipping_geometry="NONE", 
                      maintain_clipping_extent="MAINTAIN_EXTENT")
# get the ratio
raster_hc = arcpy.RasterToNumPyArray(folder_output + "//" + canopy_height_alined_name, nodata_to_value=np.nan)
raster_wh = raster_cw/raster_hc
WriteTiffData(folder_output, "Canopy_W_H", fc_dims[0], fc_dims[1], raster_wh, fc_img_geo, fc_img_prj)

# 7. One layer temperature
# read temperature information
raster_tmp = arcpy.RasterToNumPyArray(file_tmp, nodata_to_value=np.nan)
(res_x,res_y) = TellResolution(file_tmp)
[tmp_dims,tmp_img_geo,tmp_img_prj] = TellTheGeoInfo(file_tmp)
extent_tmp = TellExtent(file_tmp)
# upscale temperature
raster_tmp = (raster_tmp**2)**2
WriteTiffData(folder_output, "Tmp_Energy", tmp_dims[0], tmp_dims[1], raster_tmp, tmp_img_geo, tmp_img_prj)
# resize the temperature image by "resample"
cellsize = str(resolution_tmp)+" "+str(resolution_tmp)
arcpy.Resample_management(in_raster=folder_output + "\\Tmp_Energy.tif", 
                          out_raster=folder_output + "\\Tmp_Energy_res.tif", 
                          cell_size=cellsize, 
                          resampling_type="BILINEAR")
# Align the image
tmp_energy_alined_name = "Tmp_Energy_Alined.tif"
arcpy.Clip_management(in_raster=folder_output + "\\" + "Tmp_Energy_res.tif", 
                      rectangle=extent_LAI, 
                      out_raster=folder_output + "\\" + tmp_energy_alined_name, 
                      in_template_dataset=file_LAI, 
                      nodata_value="-3.402823e+38", 
                      clipping_geometry="NONE", 
                      maintain_clipping_extent="MAINTAIN_EXTENT")
# Upgrade resolution from 0.6 meter to 3.6 meter
arcpy.gp.Aggregate_sa(folder_output + "\\" + tmp_energy_alined_name, 
                      folder_output + "\\tmp_energy_alined_aggregate.tif", 
                      threshold_thermal_upscale_ratio, 
                      "MEAN", "EXPAND", "DATA")
# read the data and information
raster_tmp_k = arcpy.RasterToNumPyArray(folder_output + "\\tmp_energy_alined_aggregate.tif", nodata_to_value=np.nan)
raster_tmp_k = np.sqrt(np.sqrt(raster_tmp_k))
raster_tmp_k = raster_tmp_k + 273.15
(res_x,res_y) = TellResolution(folder_output + "\\tmp_energy_alined_aggregate.tif")
[tmp_dims,tmp_img_geo,tmp_img_prj] = TellTheGeoInfo(folder_output + "\\tmp_energy_alined_aggregate.tif")
extent_tmp = TellExtent(folder_output + "\\tmp_energy_alined_aggregate.tif")
# write the array as image
WriteTiffData(folder_output, "Temperature_K", tmp_dims[0], tmp_dims[1], raster_tmp_k, tmp_img_geo, tmp_img_prj)

# 8. Two-layer temperature
# resample the 0.6 by 0.6 meter thermal data (energy level) into 0.1 by 0.1 meter thermal data
arcpy.Resample_management(in_raster=folder_output + "\\Tmp_Energy_Alined.tif", 
                          out_raster=folder_output + "\\Tmp_Energy_small.tif", 
                          cell_size=str(resolution_tmp_2t)+" "+str(resolution_tmp_2t),
                          resampling_type="BILINEAR")
# prepare it ready as thermal data in degree C
# get geo-info from the resampled image
(res_x,res_y) = TellResolution(folder_output + "\\Tmp_Energy_small.tif")
[tmp_dims,tmp_img_geo,tmp_img_prj] = TellTheGeoInfo(folder_output + "\\Tmp_Energy_small.tif")
extent_tmp = TellExtent(folder_output + "\\Tmp_Energy_small.tif")
# downscale the array: from energy to the unit in degree C
raster_tmp_scale = arcpy.RasterToNumPyArray(folder_output + "\\Tmp_Energy_small.tif", nodata_to_value=np.nan)
raster_tmp_scale = np.sqrt(np.sqrt(raster_tmp_scale))
raster_tmp_scale = raster_tmp_scale
# write the array as an image in degree C
WriteTiffData(folder_output, "Temperature_C", tmp_dims[0], tmp_dims[1], raster_tmp_scale, tmp_img_geo, tmp_img_prj)
# run the temperature-separation function to get the result
CanopySoilTemperatureSeparation_Vine(file_LAI, folder_output+"\\Red.tif", folder_output+"\\NIR.tif", folder_output + "\\Temperature_C.tif",
                                     np.nan, threshold_veg, threshold_soil,
                                     folder_output, "Temperature_2L_K.tif")

# 9. Check the dimension of the outputs
# Dimension for different images should be the same
raster_1 = arcpy.RasterToNumPyArray(folder_output + "//Fractional_Cover.tif", nodata_to_value=-9999)
print("Dimension of the fractional cover:",raster_1.shape)
raster_2 = arcpy.RasterToNumPyArray(folder_output + "//Canopy_Height.tif", nodata_to_value=-9999)
print("Dimension of the canopy height:",raster_2.shape)
raster_3 = arcpy.RasterToNumPyArray(folder_output + "//Canopy_W_H.tif", nodata_to_value=-9999)
print("Dimension of the canopy height:",raster_3.shape)
raster_4 = arcpy.RasterToNumPyArray(folder_output + "//Temperature_K.tif", nodata_to_value=-9999)
print("Dimension of the canopy height:",raster_4.shape)
raster_5 = arcpy.RasterToNumPyArray(folder_output + "//Temperature_2L_K.tif", nodata_to_value=-9999)
print("Dimension of the canopy height:",raster_5.shape)