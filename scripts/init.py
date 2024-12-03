import os
import shutil

def clear_folder(folder_path, ispycache = False): # ispycache用于只删除__pycache__文件夹的情况
    rets = []
    if os.path.exists(folder_path):
        if not ispycache:
            if os.listdir: # 也许可以不要这个
                try:
                    for item in os.listdir(folder_path):
                        item_path = os.path.join(folder_path,item)
                        if os.path.isfile(item_path):
                            os.unlink(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path) # 如果是文件夹，递归删除
                except Exception as e:
                    rets.append(f"{folder_path}初始化失败:{e}")
                else:
                    rets.append(f"{folder_path}初始化完成")
            else:
                rets.append(f"{folder_path}为空")
        else:
            for item in os.listdir(folder_path):
                if item == '__pycache__':
                    shutil.rmtree(os.path.join(folder_path,item))
            rets.append(f"{folder_path}初始化完成")
    
    return rets
