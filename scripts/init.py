import os
import shutil

def clear_folder(folder_path):
    rets = []
    if os.path.exists(folder_path):
        if os.listdir:
            try:
                for item in os.listdir(folder_path):
                    item_path = os.path.join(folder_path,item)
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
            except Exception as e:
                rets.append(f"{folder_path}初始化失败:{e}")
            else:
                rets.append(f"{folder_path}初始化完成")
        else:
            rets.append(f"{folder_path}为空")    
    
    return rets
