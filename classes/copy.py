
#
# Script para Executar backup do servidor
# Classe para manipular o snapshot e a copia dos arquivos
#
# Autor......: Gustavo Marucci <gustavo@marucciviana.com.br>
# Date.......: 19/03/2024
#

import os
import shutil
import psutil

from typing     import Tuple
from win32com   import client as WMIClient


class Copy(object):
    
    snapshot    = None
    def __init__(self, drive_letter):
        '''
        Método Construtor
        
        '''
        self.drive_letter = f"{drive_letter}\\" if "\\" not in drive_letter else drive_letter


    def create_snapshot(self) -> str | None:
        '''
        create_snapshot
        Cria um diskshadow snapshot

        '''

        if self.snapshot:
            self.delete_snapshot()
        
        try:
            wmi         = WMIClient.GetObject("winmgmts:\\\\.\\root\\cimv2:Win32_ShadowCopy")
            method      = wmi.Methods_("Create")

            parameters  = method.InParameters
            parameters.Properties_[1].value = self.drive_letter

            result      = wmi.ExecMethod_("Create", parameters)
            snapshot_id = result.Properties_["ShadowID"].value

            self.snapshot = WMIClient.GetObject(f"winmgmts:\\\\.\\root\\cimv2:Win32_ShadowCopy.ID='{snapshot_id}'")
            return snapshot_id

        except Exception as e:
            print(f"Ocorreu um problema ao tentar criar um snapshot do disco. A mensagem foi: {str(e)}")
            return None

    def delete_snapshot(self) -> str | None:
        '''
        delete_snapshot
        Exclui o diskshadow snapshot

        '''
        try:
            # Não há snapshots a serem excluidos
            if not self.snapshot: return None

            # Obter ID do snapshot
            snapshot_id = self.snapshot.Properties_['ID'].value

            wmi = WMIClient.GetObject("winmgmts:\\\\.\\root\\cimv2")
            query = f"SELECT * FROM Win32_ShadowCopy WHERE ID = '{snapshot_id}'"
            snapshot = wmi.ExecQuery(query)
    
            if snapshot:
                for s in snapshot:
                    s.Delete_()
            
            self.snapshot = None
            return snapshot_id
        
        except Exception as e:
            print(f"Ocorreu um problema ao tentar excluir um snapshot do disco. A mensagem foi: {str(e)}")
            return None
        

    def clear_all_snapshots(self) -> bool:
        '''
        clear_all_snapshots
        Apaga todos os snapshots do sistema

        '''
        try:
            wmi         = WMIClient.GetObject("winmgmts:\\\\.\\root\\cimv2")
            query       = f"SELECT * FROM Win32_ShadowCopy"
            snapshots   = wmi.ExecQuery(query)
    
            if snapshots:
                for s in snapshots:
                    print(f"Apagando Snapshot ID '{s.Properties_['ID'].value}'...")
                    s.Delete_()
            
            return True
        
        except Exception as e:
            print(f"Ocorreu um problema ao tentar excluir um snapshot do disco. A mensagem foi: {str(e)}")
            return False


    def detect_removible_disk(self) -> str | None:
        '''
        detect_removible_disk
        Detecta se há um HD removivel instalado no dispositivo

        '''
        partition = psutil.disk_partitions(all=True)
                
        for p in partition:
            if 'removable' in p.opts:
                return p.device

        return None


    def run(self, origin_path: str, destination_path: str):
        '''
        run
        Copia os arquivos do snapshot para o destino

        '''
        try:
            # Checa se existe um snapshot criado
            if not self.snapshot:
                snapshot_id = self.create_snapshot()

            if not snapshot_id:
                raise Exception("Não consegui criar um snapshot")
            
            # Checa se há um disco removivel instalado
            backup_disk = self.detect_removible_disk()
            if not backup_disk:
                raise Exception("Não consegui detectar um HD para fazer backup")  
            else:
                backup_disk = backup_disk[:2]  
       
            # Remove o diretório de destino se ele já existir
            if os.path.exists(f"{backup_disk}{destination_path}"):
                shutil.rmtree(f"{backup_disk}{destination_path}")
            
            # Pega o volume do Snapshot
            snapshot_volume = self.snapshot.Properties_["DeviceObject"].value
        
            # Faz a cópia
            shutil.copytree( f"{snapshot_volume}{origin_path}", f"{backup_disk}{destination_path}")

            # Apaga o snapshot criado
            self.delete_snapshot()
            return True, None

        except Exception as e:
            msg = f"Ocorreu um problema ao tentar copiar de '{self.drive_letter[:2]}{origin_path}' para '{destination_path}'. A mensagem foi: {str(e)}"
            return False, msg
