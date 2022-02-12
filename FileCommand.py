import os
import sys
import json

from datetime import datetime
from pathlib import Path

from rich import print
from rich import box

from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.prompt import Confirm
from rich.tree import Tree
from rich.console import Console
from rich.console import Group
from rich.filesize import decimal

from type_color import TYPE_COLOR


CONFIG_NAME = 'config.json'
FORMAT_DATA = "%d/%m/%y %H:%M"

WIN = sys.platform.startswith("win")
LINUX = sys.platform.startswith("linux")

path_cwd = Path.cwd()
PATH_CONFIG = path_cwd / CONFIG_NAME

file = open(PATH_CONFIG)
CONFIG = json.load(file)
file.close()

# CONFIG_LAYOUT =     _get_val_config("layout", "[Group(A, B), C, D]")

def _panel(body, title="", expand=True):
    return(
        Panel(
            body, 
            title=title, 
            expand=expand, 
            border_style="green", padding=(0,0))
    )
    

def _get_extension_name(name):
    if name.lower() in TYPE_COLOR:
        return f"[{TYPE_COLOR[name.lower()]}]{name}[/]"
    return name


def trim_name(name, num=35):
    if num != None and len(name) > num:
        return f'{name[:num]}...'
    return name


def _set_icon_folder_name(name):
    if name.is_dir():
        return f':open_file_folder: {trim_name(name.name)}'
    if name.name == ".gitignore":
        return f'[size=12]:gear:[/]{trim_name(name.name)}'
    return trim_name(name.name)


def _get_val_config(obj, key, default=None):
    if key in obj:
        return obj[key]
    return default

_console = Console()

class FileCommand:

    def __init__(self, doc_help):

        self.doc_help = doc_help

        self.config = CONFIG
        self.current_dir =       Path(_get_val_config(CONFIG, "last_dir", ".")).resolve()
        self.config_workspaces = _get_val_config(CONFIG, "workspaces", [])
        
        self.ui_sidebar = ""
        self.ui_body = ""
        self.ui_workspaces = ""
        self.ui_current_dir = ""
        
        self.array_of_current_folder = []


    def go_folder(self, num):

        if num < 0:
            path = '\\'.join(str(self.current_dir).split("\\")[:abs(num)])
            if num == -1:
                path = f"{path}\\"
        else:
            path = self.array_of_current_folder[num-1]

        path = Path(path)

        if path.is_dir(): 
            # self.current_dir = path
            self.update_content(path)
        else:
            if Confirm.ask(f"Open file: {path.name} ?"):
                self.open_files([num])


    def go_back(self):
        l = len(str(self.current_dir).split("\\"))
        if l > 1:
            self.go_folder(-l + 1)

    
    def get_current_dir(self):
        tree = Tree(
            f":open_file_folder: Current dir", guide_style="bright_blue",
        )

        arr_HEADER = str(self.current_dir).split("\\")
        for index, item in enumerate(arr_HEADER):
            if index+1 == len(arr_HEADER):
                tree.add(f"[bold blue]{item}\\")
                continue    
            tree.add(f"[yellow]|-{index+1}|[/][bold blue]{item}\\")

        self.ui_current_dir = tree
        return tree

    
    def workspaces(self):
        if len(self.config_workspaces) == 0:
            return "No workspaces"

        tree = Tree(
            f":open_file_folder: Workspaces", guide_style="bright_blue",
        )

        for index, item in enumerate(self.config_workspaces):
            tree.add(f"{index+1}[bold blue]: [link file://{item['path']}]{item['name']}")

        self.ui_workspaces = tree
        return(tree)


    def find_el_workspace(self, name):
        for index, item in enumerate(self.config['workspaces']):
            if item['name'] == name:
                return index
        return -1


    def set_workspace(self, workspaces):
        path = str(self.current_dir) if len(workspaces) == 1 else workspaces[1]
        el = self.find_el_workspace(workspaces[0])

        if el == -1:  
            self.config['workspaces'].append({
                'name': workspaces[0],
                'path': path           
            })
        else:
            self.config['workspaces'][el]['path'] = path

        self.update_config()

    
    def go_workspace(self, int):
        self.update_content(Path(self.config_workspaces[int-1]['path']))


    def show_workspace(self):
        self.ui_workspaces = json.dumps(self.config_workspaces, indent=4)
        

    def delete_workspace(self, int): 
        self.config['workspaces'].pop(int-1)
        self.update_config()


    def open_files(self, indexes):

        paths = [f'"{str(self.array_of_current_folder[i - 1])}"' for i in indexes]

        self.ui_sidebar = '\n'.join(["Opened:", *paths])
        
        if WIN:
            os.system(f"explorer {' & '.join(paths)}")
        if LINUX:
            os.system(f"open {' '.join(paths)}")


    def get_table(self, directory_path=None):

        if directory_path is None:
            directory_path = self.current_dir    
        
        self.array_of_current_folder = []
        
        table = Table(expand=False, style="#99A799", box=box.ROUNDED, show_lines=True)    

        table.add_column("ID", justify="right", style="white", no_wrap=True)
        table.add_column("Type", justify="left", style="white")
        table.add_column("Name", justify="left", style="white", no_wrap=True)
        table.add_column("Date modified", style="yellow")
        table.add_column("Size", justify="right", style="white")

        self.array_of_current_folder = Path(directory_path).iterdir()
        self.array_of_current_folder = sorted(self.array_of_current_folder, key=lambda path: (path.is_dir(), path.suffix[1:], path.stat().st_mtime, path.name), reverse=True) 

        for index, item in enumerate(self.array_of_current_folder):
            # self.array_of_current_folder.append(item)
            file_size = decimal(item.stat().st_size) if not item.is_dir() else ""
            item_type = "" if item.is_dir() else _get_extension_name(item.suffix[1:])
            date = datetime.fromtimestamp(item.stat().st_mtime).strftime(FORMAT_DATA)
            table.add_row(str(index+1), item_type, _set_icon_folder_name(item), str(date), file_size)

        
        self.ui_body = table
        return table


    def update_config(self):
        file = open(PATH_CONFIG, "w")
        json.dump(self.config, file, indent = 4)      
        file.close()
        
        self.config_workspaces = _get_val_config(self.config, "workspaces", [])
        self.workspaces()


    def update_content(self, dir_path):
        
        """Update the current dir and ui_body"""

        self.current_dir = dir_path
        self.get_table(dir_path)
        self.get_current_dir()
        self.ui_sidebar = ""

    
    def help(self):

        """DOC"""
        
        self.ui_sidebar = self.doc_help


    def exit(self):
        sys.exit()


    def clear(self):
        os.system('clear' if os.name == "posix" else "cls")

    
    def UI(self):
        A = _panel(self.ui_current_dir if self.ui_current_dir != "" else self.get_current_dir(), expand=False)
        B = _panel(self.ui_workspaces if self.ui_workspaces != "" else self.workspaces(), expand=False)
        C = self.ui_body if self.ui_body != "" else self.get_table()
        D = self.ui_sidebar
        print(
            Columns([Group(A, B), C, D], expand=False, align="left")
        )

    
    def INPUT(self):
        return _console.input("[bold yellow]=>[/] ").split(" ")

    
    def command(self, name):
        if name in dir(self):
            return getattr(self, name)





         