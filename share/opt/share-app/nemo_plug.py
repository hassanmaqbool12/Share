import os

def create(path):
    savepath = os.path.expanduser("~/.local/share/nemo/actions/")
    os.makedirs(savepath, exist_ok=True)

    content = f'''
[Nemo Action]

Name=Share it

Comment=Share this file

Exec=bash -c 'cd {path} && python3 nemoApp.py %F'

Selection=S

Single=True

Icon-Name=emblem-shared-symbolic

Extensions=any;
'''
    with open(os.path.join(savepath, f"share.nemo_action"), 'w') as f:
        f.write(content)

path = os.path.dirname(__file__)
print(path)