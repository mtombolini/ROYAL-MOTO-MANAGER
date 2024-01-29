from datetime import datetime

def reformat_strftime(strf_date: str, from_format: str, to_format: str) -> str:
    parsed_date = datetime.strptime(strf_date, from_format)
    reformated_date = parsed_date.strftime(to_format)
    return reformated_date

fecha_creacion = datetime(2023, 11, 9, 22, 0)
print(fecha_creacion)
