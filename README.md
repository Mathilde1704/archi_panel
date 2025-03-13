# ArchiPanel
Designing architectural ideotypes of grapevines in the context of climate change using the Functional-Structural Plant
Model HydroShoot [(Albasha et al., 2019)](https://doi.org/10.1093/insilicoplants/diz007).


# Installation

1. Create a conda environment for the HydroShoot model


    conda create -n MyEnvName -c openalea3 -c conda-forge openalea.hydroshoot=5.2.0
	
    conda activate MyEnvName

2. Go to the repository where you would like to clone the 'archi_panel' project
and perform the cloning using, for example, the https url


    cd ~/<YourLocalDirectory>
    git clone https://github.com/Mathilde1704/archi_panel.git

3. Go into the 'archi_panel' directory and install the package


    cd archi_panel
	
    pip install -e .
