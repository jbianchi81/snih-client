import json
import requests
import pandas
from typing import TypedDict, Union, Literal, List, _TypedDictMeta, Tuple
import argparse
from datetime import datetime, timezone
import re
import logging

base_url = "https://snih.hidricosargentina.gob.ar/"

class EstacionSNIH(TypedDict):
    __type: str
    Codigo: int
    Descripcion: str
    Regional: int
    Sistema: int
    Cuenca: int
    Red: int
    Subcuenca: Union[str, None] 
    Provincia: int
    Rio: Union[str, None]
    Lugar: str
    Poblado: str
    Area: int
    Cota: int
    Latitud: float
    Longitud: float
    MesHidrologico: int
    NivelPsicrometrico: float
    Ventilador: bool
    Alta: datetime
    Baja: datetime
    CeroEscala: float
    SistemaCota: int
    AfluenteDe: Union[str, None]
    EsNavegable: str
    Departamento: Union[str, None]
    DistanciaDesembocadura: str
    Habilitada: bool
    Tipo: str
    Transmision: str
    ModoDeLlegar: str
    Actual: str
    RegistroValidoHasta: datetime
    Autor: int
    Registro: datetime

class CodigoMedicion(TypedDict):
    __type: str
    Tipo: int
    Codigo: int
    Descripcion: str
    Abreviatura: str
    Unidad: str
    Magnitud: int
    Dato: int
    Decimales: int
    CodigoReferencia: int
    DerechoMinimoRegistro: int
    AgrupacionesPosibles: int
    Actual: str
    RegistroValidoHasta: datetime
    Autor: str
    Registro: datetime

class Asociacion(TypedDict):
    __type: str
    Estacion: int
    Codigo: int
    Desde: datetime
    Hasta: datetime
    Minimo: int
    Maximo: int
    TipoValidacion: int
    Actual: str
    RegistroValidoHasta: datetime
    Autor: int
    Registro: datetime

class Medicion(TypedDict):
    ExtensionData: dict
    Codigo: int
    FechaHora: datetime
    NombreCodigo: str
    Valor: float

class AsociacionMedicion(Asociacion, CodigoMedicion):
    pass

class RegistroMedicion(TypedDict):
    ExtensionData: dict
    Codigo: int
    Valor: int

class Registro(TypedDict):
    ExtensionData: dict
    FechaHora: datetime
    Mediciones: List[RegistroMedicion]

class RegistroFlat(TypedDict):
    ExtensionData: dict
    FechaHora: datetime
    Codigo: int
    Valor: int

class RegistroHistorico(TypedDict):
    FechaHora: datetime
    Medicion: float
    Calificador: str
    Validado: bool

#### WMDR classes ####


class gmlPoint(TypedDict):
    pos : str # Coordinates in CRS order (usually lon lat)
    _srsName : Union[None, str] # Reference to spatial reference system (e.g. EPSG:4326 for WGS 84)

class WMDRGeospatialLocation(TypedDict):
    geoLocation : gmlPoint
    geopositioningMethod : Union[None,str]
    coordinateReferenceSystem : Union[None,str]

class WMDRObservingFacility(TypedDict):
    responsibleParty : str
    geospatialLocation : List[WMDRGeospatialLocation] # **3-07 Geospatial location (M)** | EstacionSNIH->Longitud, EstacionSNIH->Latitud EstacionSNIH->Cota |
    description : Union[None,str]
    identifier : Union[None,str]
    _id : str
    name : Union[None,str]
    facilityType : str
    belongsToSet : Union[None,str] # # 3-10 Station/platform cluster (O) | aplica? | SNIH - AR
    dateEstablished : Union[None, datetime]
    # observations : List[WMDRObservation]
    timeZone : str
    dateClosed : Union[None, datetime]
    wmoRegion : str # 3-01 Region of origin of data (C) | southAmerica 	South America | https://codes.wmo.int/wmdr/_WMORegion
    territory : str # 3-02 Territory of origin of data (C) | ARG 	Argentina | https://codes.wmo.int/wmdr/_TerritoryName
    programAffiliation : Union[None,str]
    climateZone : Union[None,str]

class WIGOSMetadataRecord(TypedDict):
    facility : List[WMDRObservingFacility]
    facilitySet : List[str]
    # observation : List[ObservationCollection]

def requestPostWithHeaders(url : str, body : Union[dict, None] = None) -> requests.Response:
    return requests.post(
        url,
        json = body,
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Length": "0",
            "Content-Type": "application/json; charset=utf-8"
        }
    )

def parseResponseList(response : requests.Response, list_property : Union[str, List[str]] = "d", caller : str = "", schema : _TypedDictMeta = None) -> list:
    if response.status_code != 200:
        raise requests.exceptions.HTTPError("Function %s failed. Status code: %i, message: %s" % (caller, response.status_code, response.text))
    try:
        content = response.json()
    except requests.exceptions.JSONDecodeError as e:
        raise e
    if type(list_property) == list:
        data = content
        for k in list_property:
            if k not in data:
                raise ValueError("Missing property '%s' from %s response", (k, caller))        
            data = data[k]
        if type(data) is not list:
            raise ValueError("Bad type in property '%s' from %s response. Must be a list" % (",".join(list_property), caller))    
    else:
        if list_property not in content:
            raise ValueError("Missing property '%s' from %s response" % (list_property, caller))
        if type(content[list_property]) is not list:
            raise ValueError("Bad type in property '%s' from %s response. Must be a list" % (list_property, caller))
        data = content[list_property]
    data = parseColumns(data, schema) if schema is not None else data
    return data

def parseColumns(data : List[dict], schema : _TypedDictMeta) -> List[dict]:
    for item in data:
        for key, typ in schema.__annotations__.items():
            if key in item and item[key] is not None:
                if  item[key] == "":
                    item[key] = None
                elif typ in [int, float]:
                    if item[key] == -999:
                        item[key] = None
                elif typ == str:
                    if item[key] in ["--", "-", "S/D", "-999"]:
                        item[key] = None
                elif typ == datetime:
                    item[key] = dateFromEpochInStr(item[key])

    return data

def toJSONSerializable(data : List[dict], schema: _TypedDictMeta) -> List[dict]:
    for item in data:
        for key, typ in schema.__annotations__.items():
            if key in item and item[key] is not None:
                if typ == datetime and type(item[key]) == datetime:
                    item[key] = item[key].isoformat()
    return data

def exportResponse(data : List[dict], output : str = None, output_format : Literal["json","csv"] = "csv", schema : _TypedDictMeta = None) -> List:
    df = pandas.DataFrame(data)
    if output is not None:
        output_dest = open(output, "w", encoding="utf-8")
        if output_format.lower() == "json":
            data = toJSONSerializable(data,schema) if schema is not None else data
            json.dump(data, output_dest, indent=2, ensure_ascii=False)
        elif output_format.lower() == "csv":
            df.to_csv(output_dest, index=False, encoding="utf-8")
        else:
            raise ValueError("Invalid format. Valid values: 'csv', 'json'")

def flattenRecord(record : Registro) -> List[RegistroFlat]:
    return [
        {
            "ExtensionData": record["ExtensionData"],
            "FechaHora": record["FechaHora"],
            "Codigo": m["Codigo"],
            "Valor": m["Valor"]
        } for m in record["Mediciones"]
    ]

def dateFromEpochInStr(datestr : str) -> datetime:
    # "/Date(1703185987000)/"
    match = re.search(r"\d+", datestr)
    if not match:
        raise ValueError("Invalid date string")
    epoch = int(match.group())
    return datetime.fromtimestamp(epoch / 1000, tz=timezone.utc)

def retrieveParseSave(api_method : str, output : str = None, output_format : Literal["json","csv"] = "csv", data_property : str = "d", params : dict = None, schema : _TypedDictMeta = None) -> List[dict]:
    response = requestPostWithHeaders("%s%s" % (base_url, api_method), params)
    data = parseResponseList(response, data_property, api_method, schema = schema)
    exportResponse(data, output, output_format, schema = schema)
    return data

def leerEstaciones(output : str = None, output_format : Literal["json","csv"] = "csv") -> List[EstacionSNIH]:
    return retrieveParseSave("Filtros.aspx/LeerEstaciones", output, output_format, schema = EstacionSNIH)

def leerCodigosMedicion(output : str = None, output_format : Literal["json","csv"] = "csv") -> List[CodigoMedicion]:
    return retrieveParseSave("MuestraDatos.aspx/LeerCodigosMedicion", output, output_format, schema = CodigoMedicion)

def leerListaAsociaciones(output : str = None, output_format : Literal["json","csv"] = "csv") -> List[Asociacion]:
    return retrieveParseSave("MuestraDatos.aspx/LeerListaAsociaciones", output, output_format, schema = Asociacion)

def leerDatosActuales(estacion : int, output : str = None, output_format : Literal["json","csv"] = "csv") -> List[Medicion]:
    return retrieveParseSave(
        "MuestraDatos.aspx/LeerDatosActuales", 
        output, 
        output_format,
        data_property=["d","Mediciones"], 
        params={"estacion": str(estacion)},
        schema = Medicion)

def leerUltimosRegistros(
        site : int, 
        var : int, 
        begin_date : datetime, 
        end_date : datetime, 
        output : str = None, 
        output_format : Literal["json","csv"] = "csv"
        ) -> List[RegistroFlat]:
    response = requestPostWithHeaders(
        "%s%s" % (base_url, "MuestraDatos.aspx/LeerUltimosRegistros"), 
        body={
            "estacion": str(site),
            "codigo": str(var),
            "fechaDesde": begin_date.strftime("%Y-%m-%d"),
            "fechaHasta": end_date.strftime("%Y-%m-%d")
        })
    data = parseResponseList(response, ["d","Mediciones"], "MuestraDatos.aspx/LeerUltimosRegistros")
    data_flat = [] 
    for r in data:
        data_flat.extend(flattenRecord(r))
    data_flat = parseColumns(data_flat, schema = RegistroFlat)
    exportResponse(data_flat, output, output_format, schema = RegistroFlat)
    return data_flat

def leerDatosHistoricos(
        site : int, 
        var : int, 
        begin_date : datetime, 
        end_date : datetime,
        validated : bool = True,
        output : str = None, 
        output_format : Literal["json","csv"] = "csv"
        ) -> List[RegistroHistorico]:
    return retrieveParseSave(
        "MuestraDatos.aspx/LeerDatosHistoricos", 
        output, 
        output_format,
        data_property=["d","Mediciones"], 
        params={
            "estacion": str(site),
            "codigo": str(var),
            "fechaDesde": begin_date.strftime("%Y-%m-%d"),
            "fechaHasta": end_date.strftime("%Y-%m-%d"),
            "validados": validated
        },
        schema=RegistroHistorico)

def harvestMetadata() -> Tuple[List[EstacionSNIH],List[CodigoMedicion],List[Asociacion]]:
    estaciones = leerEstaciones()
    codigos_medicion = leerCodigosMedicion()
    asociaciones = leerListaAsociaciones()
    return estaciones, codigos_medicion, asociaciones

### WMDR functions ###

def getClimateZone(lon : float, lat : float) -> str:
    # TODO
    # Codelist: https://codes.wmo.int/wmdr/_ClimateZone
    return None


def snihToWmdr(estacion : EstacionSNIH, asociaciones : List[AsociacionMedicion]) -> WIGOSMetadataRecord:
    ## 1 Observed variable
    #     **1-01 Observed variable - measurand (M)**| CodigoMedicion->Descripcion | https://codes.wmo.int/wmdr/_ObservedVariableTerrestrial https://codes.wmo.int/wmdr/_ObservedVariableAtmosphere

    # 1-02 Measurement unit (O) | CodigoMedicion->Unidad | https://codes.wmo.int/wmdr/_unit
    # **1-03 Temporal extent (M)** | Asociacion->Desde, Asociacion->Hasta
    # **1-04 Spatial extent (M)** | EstacionSNIH->Longitud, EstacionSNIH->Latitud, EstacionSNIH->Cota
    # 1-05 Representativeness (O) | aplica? | https://codes.wmo.int/wmdr/_Representativeness

    observing_facility : WMDRObservingFacility = {
        "wmoRegion": "southAmerica",
        "territory": "ARG",
        "name": estacion["Descripcion"],
        "FacilityType": "landFixed",
        "identifier": str(estacion["Codigo"]),
        "geospatialLocation": {
            "geoLocation": {
                "Point": "-%f -%f %f" % (estacion["Longitud"], estacion["Latitud"], estacion["Cota"]) if estacion["Cota"] is not None else "-%f -%f" % (estacion["Longitud"], estacion["Latitud"])
            },
            "coordinateReferenceSystem": "EPSG:4326"
        },
        "communicationMethod": "unknown",
        "operatingStatus": "operational" if estacion["Habilitada"] else "nonReporting",
        "description": "Modo de llegar: %s. Distancia a desembocadura: %s" % (estacion["ModoDeLlegar"] if estacion["ModoDeLlegar"] is not None else "desconocido", estacion["DistanciaDesembocadura"] if estacion["DistanciaDesembocadura"] is not None else "desconocido"),
        "climateZone": getClimateZone(estacion["Longitud"], estacion["Latitud"]),
        "facilitySet": "SNIH - ARG"
    }
    wmdr_record : WIGOSMetadataRecord = {
        "facility": [observing_facility],
        "facilitySet": "SNIH -ARG"
    }
    return wmdr_record 


    ## 3. Station/platform
    # 3-01 Region of origin of data (C) | southAmerica 	South America | https://codes.wmo.int/wmdr/_WMORegion
    # 3-02 Territory of origin of data (C) | ARG 	Argentina | https://codes.wmo.int/wmdr/_TerritoryName
    # **3-03 Station/platform name (M)** | EstacionSNIH->Descripcion | 
    # **3-04 Station/platform type (M)** | landFixed 	Land (fixed) | https://codes.wmo.int/wmdr/_FacilityType
    # **3-06 Station/platform unique identifier (M)** | EstacionSNIH->Codigo |
    # **3-07 Geospatial location (M)** | EstacionSNIH->Longitud, EstacionSNIH->Latitud EstacionSNIH->Cota |
    # 3-08 Data communication method (O) | EstacionSNIH->Transmision | https://codes.wmo.int/wmdr/_DataCommunicationMethod
    # **3-09 Station operating status (M)** | EstacionSNIH->Habilitada | https://codes.wmo.int/wmdr/_ReportingStatus
    # 3-10 Station/platform cluster (O) | aplica? | SNIH - AR

    # 4-05 Site information (O) | EstacionSNIH->DistanciaDesembocadura EstacionSNIH->ModoDeLlegar |
    # 4-07 Climate zone (O) | Derivar de coordenadas? | https://codes.wmo.int/wmdr/_ClimateZone

def getWMDR(codigo_estacion : int, estaciones : Union[List[EstacionSNIH],None] = None, codigos_medicion : Union[List[CodigoMedicion],None] = None, asociaciones : Union[List[Asociacion],None] = None):
    estaciones = estaciones if estaciones is not None else leerEstaciones()
    codigos_medicion = codigos_medicion if codigos_medicion is not None else leerCodigosMedicion()
    asociaciones = asociaciones if asociaciones is not None else leerListaAsociaciones()
    df_estaciones = pandas.DataFrame(estaciones)
    df_codigos_medicion = pandas.DataFrame(codigos_medicion)
    df_asociaciones = pandas.DataFrame(asociaciones)
    estacion = df_estaciones[df_estaciones["Codigo"] == codigo_estacion]
    if not len(estacion):
        raise ValueError("'Codigo' = %i not found in sites list" % codigo_estacion)
    estacion = estacion.iloc[0].to_dict()
    asoc_of_estacion = df_asociaciones[df_asociaciones["Estacion"] == codigo_estacion]
    if not len(asoc_of_estacion):
        logging.warning("No asociaciones found for 'Estacion' = %i" % codigo_estacion)
    asoc_merge = asoc_of_estacion.merge(df_codigos_medicion, on="Codigo")
    if len(asoc_of_estacion) > len(asoc_merge):
        logging.warning("At least one variable code 'Codigo' of Asociaciones not found in CodigosMedicion: %i > %i " % (len(asoc_of_estacion), len(asoc_merge)))
    return snihToWmdr(estacion, asoc_of_estacion.to_dict())

##### cli #####

def parse_datetime(s):
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(
        f"Not a valid date: '{s}'. Use ISO (e.g. 2025-07-29T15:00:00) or yyyy-mm-dd."
    )

def parse_args():
    parser = argparse.ArgumentParser(description="Download and save SNIH metadata/data")
    parser.add_argument(
        "api_method",
        help="Metadata/data list to retrieve",
        choices=["sites","variables","observations","present-values","last-records","historical"]
    )
    parser.add_argument(
        "output_path",
        help="Path to the output file (e.g., /path/to/file.csv)"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["csv", "json"],
        default="csv",
        help="Output format: 'csv' (default) or 'json'"
    )
    parser.add_argument(
        "-s", "--site",
        type=int,
        help="site ID (required for present-values, last-records, historical)"
    )
    parser.add_argument(
        "-v", "--variable",
        type=int,
        help="variable ID (required for last-records, historical)"
    )
    parser.add_argument(
        "-b", "--begin_date",
        type=parse_datetime,
        help="begin date (required for last-records, historical)"
    )
    parser.add_argument(
        "-e", "--end_date",
        type=parse_datetime,
        help="end date (required for last-records, historical)"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    print(f"api_method: {args.api_method}")
    print(f"Output path: {args.output_path}")
    print(f"Output format: {args.format}")
    if args.api_method == "sites":
        leerEstaciones(args.output_path, args.format)
    elif args.api_method == "variables":
        leerCodigosMedicion(args.output_path, args.format)
    elif args.api_method == "observations":
        leerListaAsociaciones(args.output_path, args.format)
    elif args.api_method == "present-values":
        if args.site is None:
            raise ValueError("-s, --site is required for present-values")
        leerDatosActuales(args.site, args.output_path, args.format)    
    elif args.api_method  == "last-records":
        leerUltimosRegistros(args.site, args.variable, args.begin_date, args.end_date, args.output_path, args.format)
    elif args.api_method  == "historical":
        leerDatosHistoricos(args.site, args.variable, args.begin_date, args.end_date, output=args.output_path, output_format=args.format)
    else:
        raise ValueError("Invalid api_method")


