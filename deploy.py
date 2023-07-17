# -*- coding: utf-8 -*-


from datetime import datetime
import sys
import os


dist_path = '/root/dist.zip'
destination_path = '/usr/local/nginx/html/'


def main(package_name):
    backup_name = package_name + '_' + datetime.now().strftime('%m%d%H%M')
    print(backup_name)
    target_path = os.path.join(destination_path, package_name)
    if os.path.exists(dist_path) and os.path.exists(target_path):
    # if True:
        print('mv /root/dist.zip /root/{}.zip'.format(package_name))
        # os.system('mv /root/dist.zip /root/{}.zip'.format(package_name))
        # backup
        source_dir = os.path.join(destination_path, package_name)
        target_dir = os.path.join(destination_path, backup_name)
        print('mv {} {}'.format(source_dir, target_dir))
        # os.system('mv {} {}'.format(source_dir, target_dir))
        # unzip
        print('unzip -d {0} /root/{1}.zip'.format(destination_path, package_name))
        # os.system('unzip -d {0} /root/{1}.zip'.format(destination_path, package_name))
    else:
        print('path error')



if __name__ == '__main__':
    package_name = 'dualcarbon-web'
    if len(sys.argv) > 1:
        package_name = sys.argv[-1]
    main(package_name)
    
        
    
        


