import argparse

from FileCommand import FileCommand, print


def print_help(errmsg):
    return f'[red]{errmsg}[/]'

parser = argparse.ArgumentParser(prog='', add_help = False)
parser.error = print_help

subparsers = parser.add_subparsers(
    title='commands',
    # description='valid subcommands',
    help='additional help')


subparsers.add_parser('e', help="exit").add_argument('exit', action="store_true", help="exit cli")
subparsers.add_parser('clear', help="clear your command line").add_argument('clear', action="store_true")
parser.add_argument('-help', "-h", action="store_true")

subparsers.add_parser('g', help="go to file by index or open 1 file").add_argument('go_folder', type=int)
subparsers.add_parser('b', help="back").add_argument('go_back', action="store_true")

parser_workspace = subparsers.add_parser('w', help="your workspaces", add_help=False)
parser_workspace.error = print_help

parser_workspace.add_argument('-set-workspace', "-s", action="extend", nargs="+", help="set new or update worksapce")
parser_workspace.add_argument('-delete-workspace', "-del", type=int)
parser_workspace.add_argument('-go-workspace', "-w", type=int)
parser_workspace.add_argument('-show-workspace', "-sh", action="store_true")

subparsers.add_parser('o', help="open files by index").add_argument('open_files', action="extend", nargs="+", type=int)

DOC_HELP = """File command.

Usage:
  g <num/-num>
  o [...nums...]
  c [...nums...]

  (-h | --help)
  (-v | --version)

Commads:
  e             Exit
  clear         Clear your command line
  g             Go to file or open file
  b             Back
  o             Open files
  c             Copy            # TODO
  p             Paste           # TODO
  r             Reset copy      # TODO

Your workspaces:
  w -s          Set new or update workspaces
  w -del        Delete workspaces
  w -w          Select workspaces
  w -sh         Show workspaces (paths)

Options:
  -h --help     Show this screen.
  -v --version  Show version.   # TODO

""" 

file_command = FileCommand(DOC_HELP)


def main():
  while True:
    file_command.UI()        
    var = vars(parser.parse_args(file_command.INPUT()))
    file_command.clear()
    for key in var:
      value = var[key]
      if type(value) == bool:
        if value:
          file_command.command(key)()
      elif value != None:
          file_command.command(key)(value)


if __name__ == "__main__":
    main()
