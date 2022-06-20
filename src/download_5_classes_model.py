import urllib
import requests
import argparse
import os

class Cfg(object):
    def __init__(self):
        super(Cfg, self).__init__()
        self.model_url = ["https://github.com/DatacollectorVN/Chest-Xray-Version2/releases/download/model-2/best_model_map50.pth"]
    
    def down_model(self, destination):
        model_url = self.model_url[0]
        print ('Start to download, this process take a few minutes')
        urllib.request.urlretrieve(model_url, destination)
        print("Downloaded pretrained model- {} to-'{}'".format(model_url, destination))


def main(model_directory):
    cfg = Cfg()
    os.makedirs(model_directory, exist_ok = True)
    cfg.down_model(destination = os.path.join(model_directory, "best_model_map50.pth"))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_directory', help = 'Destination to save model', type = str,
                        default = 'models')

    args = parser.parse_args()
    main(model_directory = args.model_directory)