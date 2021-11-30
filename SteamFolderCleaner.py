import os, winreg, vdf, ctypes, sys, shutil


def get_steam_path():
    reg = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Valve\\Steam", 0, winreg.KEY_READ)
    base_path = winreg.QueryValueEx(reg, "SteamPath")[0]
    if reg == None or base_path == None:
        return []
    with open(base_path + "/steamapps/libraryfolders.vdf") as f:
        libary = vdf.load(f)["libraryfolders"].values()
        path_lists = []
        for path in libary:
            if "path" in path:
                path_lists.append(path['path'])
        f.close()
        return path_lists


def get_game_list(path):
    acf_path_list = []
    acf_app_list = []
    for file in os.listdir(path + "/steamapps"):
        if file.endswith(".acf"):
            acf_path_list.append(os.path.join(path + "/steamapps", file))

    for i in acf_path_list:
        with open(i) as f:
            acf_app_list.append(list(vdf.load(f)["AppState"].values())[5])
            f.close()
    return acf_app_list


def get_game_uninstalled_folder(path):
    uninstalled_game = []
    game_folder = path + "/steamapps/common/"
    game_list = get_game_list(path)
    game_path_list = os.listdir(game_folder)
    for game_name in game_path_list:
        if game_name not in game_list and "steam" not in game_name.lower():
            uninstalled_game.append(game_folder + game_name)
    return uninstalled_game


def get_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size / float(1048576)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == "__main__":
    if is_admin() == False:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        exit(0)
    del_list = []
    size = 0
    steam_path = get_steam_path()
    if steam_path == []:
        print("Didn't find the Steam folder")
        os.system('pause')
        exit(0)
    for game_path in steam_path:
        [del_list.append(a) for a in get_game_uninstalled_folder(game_path)]
    if len(del_list) > 0:
        for d in del_list:
            d_size = get_size(d)
            print('{:<100s}  Size: {}MB'.format(d, str(round(d_size, 2))))
            size += d_size
        print("Found " + str(round(size, 2)) + "MB in total")
    else:
        print("No junk folder were found")
        os.system('pause')
        exit(0)
    while True:
        inp = input("Are you sure you want to delete them?[y/n]\n")
        if inp.lower() == "y":
            try:
                for i in del_list:
                    shutil.rmtree(i)
            except OSError:
                print("Error")
                os.system('pause')
                exit(0)
            print("Success")
            os.system('pause')
            break
        else:
            exit(0)
