import sqlite3
import pandas as pd
import os
from azure.storage.filedatalake import DataLakeServiceClient

def export_sqlite_to_csv(db_path: str, export_dir: str, mode: str = 'skip'):
    print(f"[Exportação] Modo selecionado: {mode}")
    os.makedirs(export_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    for table in tables:
        csv_path = os.path.join(export_dir, f"{table}.csv")
        if mode == 'skip' and os.path.exists(csv_path):
            print(f"Arquivo já existe, pulando exportação: {csv_path}")
            continue
        elif mode == 'force' and os.path.exists(csv_path):
            os.remove(csv_path)
            print(f"Arquivo antigo deletado: {csv_path}")
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        df.to_csv(csv_path, index=False)
        print(f"Exportado: {csv_path}")
    conn.close()

def create_datalake_client(account_name: str, sas_token: str, filesystem_name: str):
    service_client = DataLakeServiceClient(
        account_url=f"https://{account_name}.dfs.core.windows.net",
        credential=sas_token
    )
    return service_client.get_file_system_client(filesystem_name)

def upload_files_to_datalake(local_dir: str, landing_zone_path: str, filesystem_client, mode: str = 'skip'):
    print(f"[Upload] Modo selecionado: {mode}")
    for filename in os.listdir(local_dir):
        file_path = os.path.join(local_dir, filename)
        remote_path = f"{landing_zone_path}/{filename}" if landing_zone_path else filename
        file_client = filesystem_client.get_file_client(remote_path)
        if mode == 'skip':
            try:
                file_client.get_file_properties()
                print(f"Arquivo já existe no Data Lake, pulando upload: {remote_path}")
                continue
            except Exception:
                pass
        elif mode == 'force':
            try:
                file_client.delete_file()
                print(f"Arquivo antigo deletado no Data Lake: {remote_path}")
            except Exception:
                pass
        with open(file_path, "rb") as data:
            file_client.upload_data(data, overwrite=True)
        print(f"Upload realizado: {remote_path}")
