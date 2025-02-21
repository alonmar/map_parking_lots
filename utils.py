import pandas as pd


def get_buffer(points: pd.DataFrame, radio: int):
    points = points.copy()
    C = {
        "INEGI_CRS": "PROJCS['International_Terrestrial_Reference_Frame_1992Lambert_Conformal_Conic_2SP',GEOGCS['GCS_International_Terrestrial_Reference_Frame_1992',DATUM['International_Terrestrial_Reference_Frame_1992',SPHEROID['GRS_1980',6378137,298.257222101],TOWGS84[0,0,0,0,0,0,0]],PRIMEM['Greenwich',0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic_2SP',AUTHORITY['EPSG','9802']],PARAMETER['Central_Meridian',-102],PARAMETER['Latitude_Of_Origin',12],PARAMETER['False_Easting',2500000],PARAMETER['False_Northing',0],PARAMETER['Standard_Parallel_1',17.5],PARAMETER['Standard_Parallel_2',29.5],PARAMETER['Scale_Factor',1],UNIT['Meter',1,AUTHORITY['EPSG','9001']]]"
    }
    CRS = C["INEGI_CRS"]
    CRS = CRS.replace("'", '"')
    # Se pasa a metros para hacer el buffer y luego se regresa a latitud y longitud
    points["geometry"] = points.to_crs(CRS).buffer(radio).to_crs("EPSG:4326")

    return points
