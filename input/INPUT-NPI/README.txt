#### Folder structure
INPUT-NPI/
├── README.txt
├── nml-ens
│   ├── comandos_imporantes_nlhpc.txt
│   ├── lhs_4_select.txt
│   └── yelmo_NPI-700_cubica.nml
├── NPI
│   ├── NPI-600M
│   ├── NPI-700M
│   ├── NPI-800M
│   └── NPI-900M
└── raw
    ├── climatologia-MAR
    ├── topografia-espesor
    └── topografia-espesor-mod


#### nml-ens/
Contains Yelmo configuration files, ensemble parameter files, and a useful commands

-yelmo_NPI-700_cubica.nml: Yelmo configuration file that uses the NPI-700M input data
-lhs_4_select.txt: Parameter file used by runme. In this case, it run four simulations with four different parameter sets
-comandos_imporantes.txt: Example command lines for different types of runs (only two jajaja)

#### raw/

Contains the original data used to build the Yelmo inputs.
The original topography and ice-thickness grids have a resolution of 100 m

#### raw/climatologia-MAR/

MAR climate data for Patagonia from 1940 to 2024
Atention: the temporal frequency is not the same in every file. Some variables are monthly and others are yearly.

#### raw/topografia-espesor/

Original bedrock, ice-thickness, and error data provided by Johannes. The files include an additional border extension based on SRTM data.

The file:
npi_v063_bed_20_p2_p1_m0_0.1_noBOUND_GRAV_0.01_exp_1000_consens_extend_batimetria_sanrafael.nc

also includes:
- San Rafael bathymetry from Hoppes.
- An updated area provided by Bastian from the Glacio UdeC team.

#### raw/topografia-espesor-mod/

Modified topography and ice-thickness files.
These files were created to:

- Add lakes.
- Lower the bedrock in some northern glacier tongues
- Test changes based on the topographic uncertainty (npi_v063_error_20_p2_p1_m0_0.1_noBOUND_GRAV_0.01_exp_1000_consens_extend)
    ** The surface elevation is always kept unchanged:
        So, this means: z_srf = z_bed + H_ice is always the same.
        For example:
        z_bed_1de2 = z_bed - 1/2 * sigma
        H_ice_1de2 = H_ice + 1/2 * sigma
        
        -> z_srf_1de2  =  z_bed_1de2 + H_ice_1de2
        -> z_srf_1de2  =  z_bed - 1/2 * sigma + H_ice + 1/2 * sigma
        -> z_srf_1de2  =  z_bed + H_ice
        -> z_srf_1de2  =  z_srf

        Therefore, lowering the bedrock increases the ice thickness by the same amount.

#### NPI/

Contains the final NetCDF input files used in Yelmo
This folder must be copied inside: yelmox/ice_data/

Each subfolder corresponds to one model resolution:

NPI-600M/
NPI-700M/
NPI-800M/
NPI-900M/

Each resolution folder contains:

TOPO: topography and ice thickness
CLIM: MAR climate forcing
OCEAN: ocean forcing  (all the same value)
REGIONS: model regions and masks (all the same value)

## File-name logic

The file names show how each dataset was created:

i)
...1de2... -> The glacier tongues were modified using 1/2 of the topographic error sigma
**The maximum modification is limited to: 1/2 * H_ice


ii)
...lineal.nc: The lake bed was created using a linear shape.

iii)
...cubica.nc:The lake bed was created using a cubic shape.

iv)
When the name does not contain '1de2', 'lineal', or 'cubica', then the file was created from the original data without these modifications

Example:

NPI-900M_TOPO.nc  -> Original topography
NPI-900M_TOPO_1de2_lineal.nc ->  Topography modified using 1/2*sigma and linear lake bathimetry


