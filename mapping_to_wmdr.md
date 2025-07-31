# Mapping snih to wmdr
## 1 Observed variable
wmdr | snih | codelist
--- | --- | ---
**1-01 Observed variable - measurand (M)**| CodigoMedicion->Descripcion | https://codes.wmo.int/wmdr/_ObservedVariableTerrestrial https://codes.wmo.int/wmdr/_ObservedVariableAtmosphere
1-02 Measurement unit (O) | CodigoMedicion->Unidad | https://codes.wmo.int/wmdr/_unit
**1-03 Temporal extent (M)** | Asociacion->Desde, Asociacion->Hasta
**1-04 Spatial extent (M)** | EstacionSNIH->Longitud, EstacionSNIH->Latitud, EstacionSNIH->Cota
1-05 Representativeness (O) | aplica? | https://codes.wmo.int/wmdr/_Representativeness
## 2 Purpose of observation
wmdr | snih | codelist
--- | --- | ---
2-01 Application area(s) (O) | 14 4.2 Hydrological and Terrestrial Climate Monitoring | https://codes.wmo.int/wmdr/_ApplicationArea
**2-02 Programme/network affiliation (M)** | WHOS (not in codelist?) | https://codes.wmo.int/wmdr/_ProgramAffiliation
## 3. Station/platform
wmdr | snih | codelist
--- | --- | ---
3-01 Region of origin of data (C) | southAmerica 	South America | https://codes.wmo.int/wmdr/_WMORegion
3-02 Territory of origin of data (C) | ARG 	Argentina | https://codes.wmo.int/wmdr/_TerritoryName
**3-03 Station/platform name (M)** | EstacionSNIH->Descripcion | 
**3-04 Station/platform type (M)** | landFixed 	Land (fixed) | https://codes.wmo.int/wmdr/_FacilityType
**3-06 Station/platform unique identifier (M)** | EstacionSNIH->Codigo |
**3-07 Geospatial location (M)** | EstacionSNIH->Longitud, EstacionSNIH->Latitud EstacionSNIH->Cota |
3-08 Data communication method (O) | EstacionSNIH->Transmision | https://codes.wmo.int/wmdr/_DataCommunicationMethod
**3-09 Station operating status (M)** | EstacionSNIH->Habilitada | https://codes.wmo.int/wmdr/_ReportingStatus
3-10 Station/platform cluster (O) | aplica? | SNIH - AR
## 4. Environment
wmdr | snih | codelist
--- | --- | ---
4-01 Surface cover (O) | null | https://codes.wmo.int/wmdr/_SurfaceCoverUMD
4-02 Surface cover classification scheme (C) | null | https://codes.wmo.int/wmdr/_SurfaceCoverClassification
4-03 Topography or bathymetry (O) | null | https://codes.wmo.int/wmdr/_TopographicContext
4-04 Events at observing facility (O) | null | https://codes.wmo.int/wmdr/_EventAtFacility
4-05 Site information (O) | EstacionSNIH->DistanciaDesembocadura EstacionSNIH->ModoDeLlegar |
4-06 Surface roughness (O) | null | https://codes.wmo.int/wmdr/_SurfaceRoughnessDavenport
4-07 Climate zone (O) | Derivar de coordenadas? | https://codes.wmo.int/wmdr/_ClimateZone
## 5. Instruments and methods of observation
wmdr | snih | codelist
--- | --- | ---
**5-01 Source of observation (M)** | automaticReading Instrumental automatic reading o manualReading Instrumental manual reading, derivar de EstacionSNIH->Transmision y CodigoMedicion->Tipo | https://codes.wmo.int/wmdr/_SourceOfObservation
**5-02 Measurement/observing method (M)** | Derivar de CodigoMedicion->Descripcion | https://codes.wmo.int/wmdr/_ObservingMethodTerrestrial https://codes.wmo.int/wmdr/_ObservingMethodAtmosphere 
5-03 Instrument specifications (O) | null | 
5-04 Instrument operating status (O) | ? | https://codes.wmo.int/wmdr/_InstrumentOperatingStatus
5-05 Vertical distance of sensor (C) | null | 
5-06 Configuration of instrumentation (C) | null |
5-07 Instrument control schedule (O) | null |
5-08 Instrument control result (C) | null |
5-09 Instrument model and serial number (O) | null |
5-10 Instrument routine maintenance (O) | null |
5-11 Maintenance party (O) | null | 
5-12 Geospatial location (C) | null |
5-13 Maintenance activity (O) | null |
5-14 Status of observation (O) | null |
## 6. Sampling
wmdr | snih | codelist
--- | --- | ---
7-01 Data-processing methods and algorithms (O) | null |
7-02 Processing/analysis centre (O) | null |
**7-03 Temporal reporting period (M)** | derivar de EstacionSNIH->Transmision |
7-04 Spatial reporting interval (C) | null |
7-05 Software/processor and version (O) | null |
7-06 Level of data (O) | level2 Level II | https://codes.wmo.int/wmdr/_LevelOfData
7-07 Data format (O) | custom JSON |
7-08 Version of data format (O) | null |
7-09 Aggregation period (O) | derivar de CodigoMedicion->Descripcion | 
7-10 Reference time (O) | null |
7-11 Reference datum (C) | EstacionSNIH->CeroEscala |
7-12 Numerical resolution (O) | null |
7-13 Timeliness (of reporting) (O) | null | 
**7-14 Schedule of international exchange (M)** | ? |
## 8. Data quality 
wmdr | snih | codelist
--- | --- | ---
8-01 Uncertainty of measurement (O) | null |
8-02 Procedure used to estimate uncertainty (C) | null |
8-03 Quality flag (O) 8-04 Quality flagging system (C) | derivar de RegistroHistorico->Validado | https://codes.wmo.int/wmdr/_WaterML2_0
8-05 Traceability (C) | null |
## 9. Ownership and data policy
wmdr | snih | codelist
--- | --- | ---
**9-01 Supervising organization (M)** | Subsecretaría de Recursos Hídricos, Ministerio de Economía, Argentina | 
**9-02 Data policy/use constraints (M)** | WMOEssential WMOEssential | https://codes.wmo.int/wmdr/_DataPolicy
## 10. Contact 
wmdr | snih | codelist
--- | --- | ---
**10-01 Contact (nominated focal point) (M)** | Metadata Editor | https://codes.wmo.int/wmdr/_WIGOSFunction
