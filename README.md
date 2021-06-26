
# AggieAir-Images-4-TSEB-PT
## Contact
- [Rui Gao](https://github.com/RuiGao92)
- Rui.Gao@usu.edu | Rui.Gao@aggiemail.usu.edu

## Brief introduction:<br>
- This python script is used for the [AggieAir](https://uwrl.usu.edu/aggieair/)-image processing to support the [TSEB-PT](https://github.com/hectornieto/pyTSEB) model.
- This repository can be used for the user who has high-resolution data, including red-band optical image, near-infrared-band optical image, DSM image, thermal image, and LAI image (map). The results contain the image to run the TSEB-PT model.
- This repository is not written in a python function since the some results from some cells can help researchers to find more information, and it is easier for users to debug when apply this script for new research objectives.

## Involved python functions:
These involved python functions are used to extract information from the corresponding inputs. They could be found in other repositories in my GitHub. Details for each function can be found there.
- `CanopyHeight_Vine`: [Vine_Info_Extraction]| canopy height at a subfield scale is generated at the end as one image.
- `TellResolution`: [Rui_Python_Functions_Package]| resolution (2 values) is generated.
- `TellTheGeoInfo`: [Rui_Python_Functions_Package]| (1) dimension, (2) geographic information, and (3) projection information of the input image are generated. 
- `FolderCreater`: [Rui_Python_Functions_Package]| a python function used to generated a folder.
- `WriteTiffData`: [Rui_Python_Functions_Package]| put required information and the array into this function, image in "Tiff" format is generated.
- `TellExtent`: [Rui_Python_Functions_Package]| the north, south, east, and west (4 values) are gained based on the input image.

## Required inputs:
- `file_grids`: the folder path of the research grids (fishnet), and the resolution I used is 3.6 meter by 3.6 meter.<br>
- `file_LAI`: the folder path of the LAI image, and the resolution is 3.6 meter by 3.6 meter.<br>
- `file_RGBN`: the folder path of the optical image, and the resolution is 0.1 meter by 0.1 meter.<br>
- `file_DSM`: the folder path of the DSM image, and the resolution is 0.1 meter by 0.1 meter.<br>
- `file_tmp`: the folder path of the thermal image, and the resolution is 0.6 meter by 0.6 meter<br>
- `threshold_veg`: this is a threshold from NDVI to define which pixel is recognized as vegetation index. This threshold varies from flight to flight, and user can get a good guess from the cell called "Generate R, G, B, NIR, and DSM images" and then re-define the threshold when you cannot get the exact threshold.<br>
- `threshold_soil`: this is similar to above one, and this NDVI threshold is used to define the soil pixel.<br>
- `threshold_veg_height`: the shortest height of the vegetation (vine-canopy height for my case).<br>
- `threshold_thermal_upscale_ratio`: the ratio between the square of the LAI pixel and the square of the thermal pixel, in string format. It is "6" for my case. 
- `resolution_grid`: the resolution for the fishnet with only one length (e.g., 3.6 meter).<br>
- `resolution_rgb_dsm`: the resolution for the optical and DSM data.<br>

## Results for TSEB-PT:
- `Canopy_Height.tif`: the map for the canopy height.
- `Canopy_W_H.tif`: the ratio between canopy width and canopy height.
- `Fractional_Cover.tif`: the fractional cover of the canopy vegetation.
- `Temperature_K.tif`: the temperature (one layer) in degree K.


## Acknokledge:<br>
Thanks for the suggestions and guidence from [Dr. Torres](https://engineering.usu.edu/cee/people/faculty/torres-alfonso)

## Citation:<br>
Please cite the paper below when you are using this script.<br>
[Evapotranspiration partitioning assessment using a machine-learning-based leaf area index and the two-source energy balance model with sUAV information](https://www.researchgate.net/publication/350820947_Evapotranspiration_partitioning_assessment_using_a_machine-learning-based_leaf_area_index_and_the_two-source_energy_balance_model_with_sUAV_information)


