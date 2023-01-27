GENOTYPES = ['danugue', 'verdiso', 'totika', 'plantdec', 'ghemra', 'staphid', 'belledenise', 'pardina', 'souzao',
             'babicacr', 'affenthale', 'hagnoszld', 'chachoub', 'opsimoe', 'chaptal', 'ichkim', 'salice', 'kvidinka',
             'morrastel', 'coarna', 'garridomac', 'petitverdo', 'raboso', 'peikani', 'mission', 'poulsard', 'mauzac',
             'negruv', 'freisa', 'graeco', 'lauzetb', 'avarengo', 'karaogla', 'ahmersalap']

SPACING_BETWEEN_ROWS = 1.  # m
SPACING_ON_ROW = 0.25  # m
ROW_ANGLE_WITH_SOUTH = 140.  # decimal degrees
DATE_BUDBURST = '2021-04-01'
UNITE_INCIDENT_RADIATION = 'Rg_Watt/m2'  # one of ("Rg_Watt/m2", "RgPAR_Watt/m2", "PPFD_umol/m2/s")
PARAMS_STOMATAL_CONDUCTANCE = {
    "model": "vpd",
    "g0": 0.02,  # mol m-2 s-1
    "m0": 5.278,  # mmol(H2O) umol-1(CO2)
    "D0": 30.0}  # kPa-1
SOIL_CLASS = 'Sand'
SOIL_DIMENSIONS = {
    "radius": 0.25,  # m
    "depth": 0.75}  # m
