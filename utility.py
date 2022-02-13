from type_color import TYPE_COLOR

from shutil import copy2

from rich.panel import Panel


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
    # suffix = str(name).split('.')[-1]
    # if suffix in ICON:
    #     return f'[size=12]:{ICON[suffix]}:[/]{trim_name(name.name)}'
    return trim_name(name.name)


def _get_val_config(obj, key, default=None):
    if key in obj:
        return obj[key]
    return default


def _get_deep_files_by_format(folder, formats):
    files = []
    for item in folder.iterdir():
        if item.is_dir():
            tmp = _get_deep_files_by_format(item, formats)
            if len(tmp) > 0:
                files.append(item)
        # elif item.suffix in formats:
        elif formats == "*":
            files.append(item)
    return files


def _copytree(src, dst, _formats):

    if src.is_dir():
        dst = dst / src.name
        if not dst.exists():
            dst.mkdir()
        for item in src.iterdir():
            if item.is_dir():
                _copytree(item, dst, _formats)
            else:
                copy2(item, dst)
    else:
        copy2(src, dst / src.name)
