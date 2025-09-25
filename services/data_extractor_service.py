import json
import os
from os import makedirs
from typing import Literal
import pandas as pd
from unidecode import unidecode

class DataExtractorService:
    

    def aggroup_itens(key, dicionario):
        tmp = {}
        for d in dicionario:
            chave = f"{d['terminal']}-{key}"
            if chave in tmp:
                tmp[chave]["anexos"].extend(d["anexos"])
            else:
                tmp[chave] = d
        return list(tmp.values())
    
    def generate_file(horario, arr_json_files):
        dir_save = os.path.join("downloads", f"TERMINAIS_{horario}")
        makedirs(dir_save, exist_ok=True)
        for arr in arr_json_files:
            filename = unidecode(arr["terminal"].split(" - ")[0].replace(" ", "_"))
            arr["list_email"] = DataExtractorService.get_emails(arr["terminal"])
            with open(
                os.path.join(dir_save, f"{filename}.json"), "w", encoding="utf8"
            ) as f:
                f.write(json.dumps(arr, indent=4))

    def get_emails(terminal):
        with open("downloads\\destinatarios.csv", encoding="utf-8") as f:
            lines_dest = f.readlines()
        lines_dest = [ld.replace("\n", "").split(";") for ld in lines_dest]
        for l in lines_dest:
            if l[0].strip() == terminal.strip():
                return l[1].split(",")

    def convert_to_csv():
        df = pd.read_excel('downloads/links_anexos_consolidados_novo 1.xlsx', header=0, sheet_name=0)
        df_destinatarios = pd.read_excel('downloads/links_anexos_consolidados_novo 1.xlsx', header=0, sheet_name=1)
        filename_save = os.path.join('downloads', 'links_anexos_consolidados.csv')
        filename_save_destintarios = os.path.join('downloads', 'destinatarios.csv')
        df.to_csv(filename_save, index=False, sep=';')
        df_destinatarios.to_csv(filename_save_destintarios, index=False, sep=';')
        return filename_save_destintarios, filename_save
    
    def data_to_dict(linha):
        colunas = linha.split(";")
        return {
            "terminal": colunas[0].strip(),
            "area_marinha": f"ÁREA {colunas[1].strip()}",
            "marine_area": f"AREA {colunas[1].strip()}",
            "horario": colunas[2],
            "anexos": [
                {
                    "nome": colunas[3].strip(),
                    "link": colunas[4].strip(),
                    "extension": "jpeg"
                    if "marinha" in colunas[4].strip()
                    else "pdf",
                }
            ],
        }
    
    def setup_data():
        _,filename_save = DataExtractorService.convert_to_csv()
        with open(filename_save, encoding="utf8") as f:
            lines = f.readlines()
        lines = [line.replace("\n", "") for line in lines]
        lines.pop(0)
        dict_setup = lambda header: {head: [] for head in header}

        horarios = list(set([line.split(";")[2].split(":")[0] for line in lines]))
        result_dict = dict_setup(horarios)
        for linha in lines:
            dados = DataExtractorService.data_to_dict(linha)
            hora = dados["horario"].split(":")[0]
            result_dict[hora].append(dados)

        for key, dicionario in result_dict.items():
            result_dict[key] = DataExtractorService.aggroup_itens(key, dicionario)

        for key, dicionario in result_dict.items():
            DataExtractorService.generate_file(key, dicionario)
