import imageio
import os, progressbar, argparse
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument("-g", type=str, help='the gif to parse', required=True)
parser.add_argument("-e", type=str, help='name of output directory', required=True)
parser.add_argument("-o", type=str, help='name of output gif', required=False)
args = parser.parse_args()

filepath = args.g
extractDir = args.e

name = args.o
if name is None:
    name = 'animation'

i = 0
images = []

def extractFrames(inGif, out):
    try:
        os.mkdir("./" + out)
    except FileExistsError:
        os.system('rm -rf ./' + out + '/*')
    frame = Image.open(inGif)
    nframes = 0
    id = 0
    while frame:
        id = str(nframes)
        if nframes < 10:
            id = '000' + id
        elif nframes < 100:
            id = '00' + id
        elif nframes < 1000:
            id = '0' + id
        frame.save( out + '/' + os.path.splitext(os.path.basename(inGif))[0] + '-' + id + '.png')
        nframes += 1
        try:
            frame.seek( nframes )
        except EOFError:
            break
    return sorted(((out + '/' + fn) for fn in os.listdir('./' + out) if fn.endswith('.png')))

def makeGIF(filenames, out, fps=60):
    with imageio.get_writer('./' + out + '.gif', mode='I', fps = fps) as writer:
        bar = progressbar.ProgressBar(maxval=len(filenames)*2, \
            widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage(), ' ', progressbar.ETA()])
        bar.start()
        i = 0
        for filename in filenames:
            image = imageio.imread(filename)
            writer.append_data(image)
            bar.update(i)
            i += 1

        first = True
        for filename in reversed(filenames):
            if not first:
                image = imageio.imread(filename)
                writer.append_data(image)
                bar.update(i)
                i += 1
            else:
                first = False

        bar.finish()

filenames = extractFrames(filepath, extractDir)

# names = sorted(((args.e + '/' + fn) for fn in os.listdir('./' + args.e) if fn.endswith('.png'))) #extractFrames(filepath, extractDir)
makeGIF(filenames, name)
