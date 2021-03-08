from PIL import Image
import PIL
import regex as re
import numpy as np
import os

print("""

██████╗░░█████╗░████████╗░█████╗░      ██╗░░██╗██╗██████╗░███████╗██████╗░
██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗      ██║░░██║██║██╔══██╗██╔════╝██╔══██╗
██║░░██║███████║░░░██║░░░███████║      ███████║██║██║░░██║█████╗░░██████╔╝
██║░░██║██╔══██║░░░██║░░░██╔══██║      ██╔══██║██║██║░░██║██╔══╝░░██╔══██╗
██████╔╝██║░░██║░░░██║░░░██║░░██║      ██║░░██║██║██████╔╝███████╗██║░░██║
╚═════╝░╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░╚═╝      ╚═╝░░╚═╝╚═╝╚═════╝░╚══════╝╚═╝░░╚═╝

Type help for a list of commands""")

def give_help(func):
    if func == None:
        print("""COMMANDS
Type any of the commands followed by 'help' for a description of what it does and a list of arguments

COMMANDS:
1) encode
2) decode
3) capacity""")
    elif func == encode:
        print("""ENCODE FUNCTION
The encode function takes an image and a file, and outputs an image with the data imperceptibly encoded within the image.

ARGS:
1) Image file path. (eg samplefolder/sampleimage.jpg)
2) Path of data to be encoded
3) (Optional) By default is the same as argument 1. Output file path (eg samplefolder/sampleimage.png). The extention must be an uncompressed format (eg bmp), or a lossless compression format (eg png)""")
    elif func == getFileCapacity:
        print("""capacity FUNCTION
This function calculates how many charectars can fit into one image

ARGS:
1) Image file path (eg samplefolder/sampleimage.jpg)""")
    elif func == decode:
        print("""DECODE FUNCTION
This function extracts the hidden data from the image and outputs it into a file

ARGS:
1) Image file path (eg samplefolder/sampleimage.jpg)""")

def getFileCapacity(image):
    size = list(np.array(Image.open(image)).shape)
    size = size[0] * size[1] * size[2]//4
    return size

def zeroLastTwoBinaryDigits(image):
    return image - image % 4

def generateNoiseFromFile(shape, name):
    datIn = open(name,"rb").read().hex()

    nm = [bin(int(datIn[i:i+2], 16))[2:] for i in range(0, len(datIn),2)]

    for i in range(len(nm)):
        while len(nm[i]) < 8:
            nm[i] = "0" + nm[i]

    nm = "".join(nm)
    nm = [np.uint8(int(nm[i:i+2], 2)) for i in range(0, len(nm),2)]
    print("[████████████████████████████████████████] 100%\nProcessing data...")
    countmax = shape[0]*shape[1]*shape[2]-len(nm)
    count = 0
    for i in range(shape[0]*shape[1]*shape[2]-len(nm)):
        nm.append(np.uint8(0))
        count += 1
        if count % int(countmax/100) == 0:
            print("[" + "█"*int(count*40/countmax) + "-"*(40-int(count*40/countmax)) + "] " + str(int(count*100/countmax)) + "%",end="\r")
    print("[████████████████████████████████████████] 100%")
    
    nm = np.array(nm).reshape(shape)

    Image.fromarray(np.uint8(nm/3*255)).save("nm.png")

    return nm

def encode(image, data, output):
    if getFileCapacity(image) < os.path.getsize(data):
        print("###ERROR### FILE TOO LARGE\nThe file", data, "(" + str(os.path.getsize(data)), "bytes) is bigger than",image + "'s max capacityity (" + str(getFileCapacity(image)) + " bytes)")
        return

    print("Preparing image for data...")
    im = zeroLastTwoBinaryDigits(np.array(Image.open(image)))
    print("Loading data...")
    out = np.add(im, generateNoiseFromFile(im.shape, data))
    print("Done. Saving...")
    out = Image.fromarray(out)
    out.save(output)
    print("Saved")

def decode(image, output):
    recover = np.array(Image.open(image))
    print("Extracting data from image...")
    recover = np.subtract(recover, zeroLastTwoBinaryDigits(recover)).reshape(1, -1)[0]
    print("Processing data...")

    binaryMappings = lambda x : ["00", "01", "10", "11"][x]
    
    recover = "".join(list(map(binaryMappings, recover)))
    
    print("Removing placeholder data...")
    recover = re.sub("(00000000)+$", "", recover)

    print("Saving data as",output + " ...")
    output = open(output,"wb")
    output.write(bytes([int(recover[i: i+8],2) for i in range(0, len(recover), 8)]))
    output.close()
    print("Saved")

while True:
    command = input("\n>> ").split()
    print()

    main = command[0]
    args = command[1:]

    if main == "encode":
        if args[0] == "help":
            give_help(encode)
        else:
            verified_args = True

            if len(args) > 3:
                print("###ERROR### ARGUMENT ERROR\nToo many arguments. Type 'encode help' for a list of arguments")
                verified_args = False
            elif len(args) < 2:
                print("###ERROR### ARGUMENT ERROR\nNot enough arguments. Type 'encode help' for a list of arguments")
                verified_args = False
            else:
                try:
                    Image.open(args[0])
                except FileNotFoundError:
                    print("###ERROR### FILE NOT FOUND\n" + args[0], "does not exist. ")
                    verified_args = False
                except PIL.UnidentifiedImageError:
                    print("###ERROR### IMAGE LOAD FAIL\n" + args[0], "is not an image. ")
                    verified_args = False
                
                try:
                    open(args[1],"rb").read()
                except FileNotFoundError:
                    print("###ERROR### FILE NOT FOUND\n" + args[1], "does not exist. ")
                    verified_args = False

            if verified_args:
                if len(args) == 2:
                    encode(args[0],args[1],args[0])
                else:
                    if len(args[2].split("/")) > 1:
                        verified_args = True
                        try:
                            testfile = open("/".join(args[2].split("/")[:-1]) + "/" + "test.txt","w").write("")
                            os.remove("/".join(args[2].split("/")[:-1]) + "/" + "test.txt")
                            if args[2].split(".")[1] in "jpg jpeg JPG".split():
                                raise AttributeError
                        except FileNotFoundError:
                            print("###ERROR### INVALID DIRECTORY\n" + "/".join(args[2].split("/")[:-1]) + "/ is an invalid directory")
                            verified_args = False
                        except AttributeError:
                            print("###ERROR### INVALID FILE EXTENTION\n" + args[2].split(".")[1] , "is a lossy compression format. Encoded data would be lost")
                    if verified_args:
                        encode(args[0], args[1], args[2])
    elif main == "decode":
        verified_args = True
        if args[0] == "help":
            give_help(decode)
            verified_args = False
        elif len(args) != 2:
            print("###ERROR### ARGUMENT ERROR\n2 arguments required")
            verified_args = False
        else:
            try:
                Image.open(args[0])
            except FileNotFoundError:
                print("###ERROR### FILE NOT FOUND\n" + args[0], "does not exist. ")
                verified_args = False
            except PIL.UnidentifiedImageError:
                print("###ERROR### IMAGE LOAD FAIL\n" + args[0], "is not an image. ")
                verified_args = False

            try:
                testfile = open("/".join(args[1].split("/")[:-1]) + "/" + "test.txt","w").write("")
                os.remove("/".join(args[1].split("/")[:-1]) + "/" + "test.txt")
            except FileNotFoundError:
                print("###ERROR### INVALID DIRECTORY\n" + "/".join(args[1].split("/")[:-1]) + "/ is an invalid directory")
                verified_args = False

        if verified_args:
            decode(args[0],args[1])
    elif main == "capacity":
        verified_args = True
        if len(args) != 1:
            print("###ERROR### ARGUMENT ERROR\n1 arguments required")
            verified_args = False
        else:
            if args[0] == "help":
                give_help(getFileCapacity)
            else:
                try:
                    Image.open(args[0])
                except FileNotFoundError:
                    print("###ERROR### FILE NOT FOUND\n" + args[0], "does not exist. ")
                    verified_args = False
                except PIL.UnidentifiedImageError:
                    print("###ERROR### IMAGE LOAD FAIL\n" + args[0], "is not an image. ")
                    verified_args = False
                if verified_args:
                    print("The file",args[0],"can fit",str(getFileCapacity(args[0])),"bytes of data")
    elif main == "help":
        give_help(None)
    else:
        print("###ERROR### UNRECOGNISED COMMAND\nType 'help' for a list of commands")
