import os
import datetime
import pytz
import csv

class FileVersion:
    def __init__(self, version, file_path, metadata):
        self.version = version
        self.file_path = file_path
        self.metadata = metadata

class Node:
    def __init__(self, version):
        self.version = version
        self.left = None
        self.right = None

#Classe que implementa o controle de versão
class VersionControlSystem:
    def __init__(self):
        self.root = None
        self.csv_file = 'versions.csv'

#função que adiciona uma nova versão ao repositorio e insere na árvore
    def commit(self, ile_fpath):
        tz = pytz.timezone('America/Sao_Paulo')
        version = datetime.datetime.now(tz).strftime("%Y%m%d%H%M%S")
        current_time = datetime.datetime.now(tz)

        metadata = self._get_file_metadata(file_path)
        if metadata:
            metadata['last_modified'] = current_time
            new_version = FileVersion(version, file_path, metadata)
            self.root = self._insert(self.root, new_version)
            self.save_to_csv()
            print("Arquivo adicionado com sucesso.")
        else:
            print("O arquivo não existe ou não pôde ser acessado. Verifique o caminho e tente novamente.")

#função que insere um novo nó na árvore
    def _insert(self, root, new_version):
        if root is None:
            return Node(new_version)

        if new_version.metadata['last_modified'] < root.version.metadata['last_modified']:
            root.left = self._insert(root.left, new_version)
        else:
            root.right = self._insert(root.right, new_version)

        return root
    
#função que escreve a nova versão no arquivo csv
    def save_to_csv(self):
        versions_data = self._get_versions_data()
        self._write_to_csv(versions_data)

#função que percorre a árvore em ordem
    def _get_versions_data(self):
        versions_data = []
        self._inorder_traversal_for_csv(self.root, versions_data)
        return versions_data
    
#função que percorre a árvore em ordem para coleta de dados
    def _inorder_traversal_for_csv(self, root, versions_data):
        if root:
            self._inorder_traversal_for_csv(root.left, versions_data)
            versions_data.append([root.version.file_path, root.version.version, root.version.metadata['last_modified']])
            self._inorder_traversal_for_csv(root.right, versions_data)

#função que escreve no arquivo csv
    def _write_to_csv(self, data):
        with open(self.csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['File Path', 'Version', 'Last Modified'])
            writer.writerows(data)

#função que obtem o tamanho dos meta dados e ultima modificação
    def _get_file_metadata(self, file_path):
        if os.path.exists(file_path):
            file_stats = os.stat(file_path)
            metadata = {
                'size': file_stats.st_size,
                'last_modified': datetime.datetime.fromtimestamp(file_stats.st_mtime)
            }
            return metadata
        else:
            return None
        
#função que exibe as versões disponiveis
    def get_all_versions(self):
        if self.root:
            self._inorder_traversal(self.root)
        else:
            print("Não existe versão disponível.")

    def _inorder_traversal(self, root):
        if root:
            self._inorder_traversal(root.left)
            formatted_time = root.version.metadata['last_modified'].strftime("%Y-%m-%d %H:%M:%S")
            print(f"Versão: {root.version.version}, Data: {formatted_time}")
            self._inorder_traversal(root.right)

#função que exclui uma versão especifica e salva no csv
    def delete_version(self, file_path, version_to_delete):
        self.root = self._delete(self.root, file_path, version_to_delete)
        self.save_to_csv()

#função que exclui um nó especifico da árvore e mantém sua propriedade 
    def _delete(self, root, file_path, version_to_delete):
        if root is None:
            return root

        if version_to_delete < root.version.version:
            root.left = self._delete(root.left, file_path, version_to_delete)
        elif version_to_delete > root.version.version:
            root.right = self._delete(root.right, file_path, version_to_delete)
        else:
            if root.version.file_path == file_path:
                if root.left is None:
                    return root.right
                elif root.right is None:
                    return root.left
                temp = self._min_value_node(root.right)
                root.version = temp.version
                root.right = self._delete(root.right, file_path, temp.version.version)
            else:
                root.left = self._delete(root.left, file_path, version_to_delete)
        return root

    def _min_value_node(self, node):
        current = node
        while current.left is not None:
            current = current.left
        return current

def command_line_interface():
    vcs = VersionControlSystem()

    while True:
        print("\nEscolha uma opção:")
        print("1. Adicionar arquivo ao repositório")
        print("2. Visualizar todas as versões disponíveis")
        print("3. Excluir uma versão específica de um arquivo")
        print("4. Sair")

        choice = input("Opção: ")

        if choice == "1":
            file_path = input("Digite o caminho do arquivo a ser adicionado: ")
            if os.path.exists(file_path):
                vcs.commit(file_path)
            else:
                print("Arquivo não encontrado. Verifique o caminho e tente novamente.")

        elif choice == "2":
            vcs.get_all_versions()

        elif choice == "3":
            file_path = input("Digite o caminho do arquivo para excluir uma versão: ")
            version_to_delete = input("Digite a versão que deseja excluir: ")
            vcs.delete_version(file_path, version_to_delete)

        elif choice == "4":
            break
        else:
            print("Escolha inválida. Tente novamente.")

if __name__ == "__main__":
    command_line_interface() 